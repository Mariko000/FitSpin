from rest_framework import generics
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Prefetch
from .forms import UserUpdateForm
from .models import LoginHistory
from tags.models import UserTag
import datetime
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Count
from .serializers import UserListSerializer
from followers.models import Follow
from blog.models import Post
import random
from followers.models import Follow, Block 
# Create your views here.

User = get_user_model()

@login_required
def profile_update(request):
    """
    ユーザープロフィールとアバター画像を更新します。
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:user_profile')
    else:
        form = UserUpdateForm(instance=request.user)
        # 初期値に既存タグを入れる
        initial_tags = ", ".join([ut.tag.name for ut in request.user.tags.all()])
        form = UserUpdateForm(instance=request.user, initial={"tags": initial_tags})
    
    return render(request, 'account/profile_update.html', {'form': form})

@login_required
def login_calendar(request):
    """
    ユーザーのログイン履歴カレンダーを表示します。
    """
    login_dates = LoginHistory.objects.filter(user=request.user).values_list('login_date', flat=True)
    login_dates_str = [d.strftime('%Y-%m-%d') for d in login_dates]
    
    context = {
        'user': request.user,
        'login_dates': login_dates_str,
    }
    return render(request, 'account/login_calendar.html', context)


@login_required
def user_profile(request):
    """
    ログイン中のユーザープロフィールを表示します。
    """
     # ログイン中のユーザーを取得
    profile_user = request.user

    # フォロワー一覧（自分をフォローしている人）
    followers = [f.follower for f in Follow.objects.filter(following=profile_user).select_related("follower")]
    # フォロー中一覧（自分がフォローしている人）
    following = [f.following for f in Follow.objects.filter(follower=profile_user).select_related("following")]

    
    # フォロワー数とフォロー数を取得
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    # タグ一覧を取得（UserTag経由でTagを取る）
    tags = [ut.tag.name for ut in profile_user.tags.all()]
    
    context = {
        'profile_user': profile_user,
        'followers_count': followers_count,
        'following_count': following_count,
        'followers': followers,
        'following': following,
        'tags': tags,
    }
    return render(request, 'account/user_profile.html', context)

def user_profile_detail(request, user_id):
    """
    他人のプロフィール
    """
    profile_user = get_object_or_404(User, id=user_id)

    followers = Follow.objects.filter(following=profile_user).select_related("follower")
    following = Follow.objects.filter(follower=profile_user).select_related("following")

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    posts = Post.objects.filter(author=profile_user).order_by("-created_at")
    user_tags = profile_user.tags.select_related("tag").all()

    context = {
        "profile_user": profile_user,
        "followers": [f.follower for f in followers],
        "following": [f.following for f in following],
        "followers_count": followers.count(),
        "following_count": following.count(),
        "is_following": is_following,
        "posts": posts,
        "user_tags": user_tags,
    }
    return render(request, "account/other_user_detail.html", context)


@login_required
def user_list_page(request):
    current_user = request.user
    
    # 全ユーザーリストを取得 (自分自身を除く)
    users = (
        User.objects.exclude(id=current_user.id)
        .annotate(
            followers_count=Count('follower_set', distinct=True),
            following_count=Count('following_set', distinct=True),
        )
        .order_by('-followers_count')
        .prefetch_related(Prefetch('tags', queryset=UserTag.objects.select_related('tag')))
    )
    
    following_ids = set(
        Follow.objects.filter(follower=current_user)
                      .values_list('following__id', flat=True)
    )
    
    # ユーザーリストにis_followingフラグを追加
    for u in users:
        u.is_following = u.id in following_ids
        u.is_blocked = u.id in blocked_ids

    # --- おすすめユーザーのロジック ---
    
    # 1. 共通フォロー (あなたがフォローしているユーザーがフォローしている人)
    following_users_ids = list(following_ids)
    
    common_followers = User.objects.filter(
        follower_set__following__in=following_users_ids
    ).exclude(
        Q(id=current_user.id) | Q(id__in=following_ids)
    ).distinct()[:5]

    # 2. 共通タグ (あなたが持っているタグと同じタグを持つユーザー)
    user_tags_ids = UserTag.objects.filter(user=current_user).values_list('tag__id', flat=True)
    common_tags = User.objects.filter(
        tags__tag__in=user_tags_ids
    ).exclude(
        Q(id=current_user.id) | Q(id__in=following_ids)
    ).distinct()[:5]

    # 3. 新規/ランダムユーザー (まだフォローしていないランダムなユーザー)
    exclude_ids = following_ids.union({current_user.id})
    all_others = User.objects.exclude(id__in=exclude_ids)
    random_users = random.sample(list(all_others), min(5, all_others.count()))
    
    # 結合して重複を排除
    recommended_users_list = list(common_followers) + list(common_tags) + list(random_users)
    unique_recommended_users = list({user.id: user for user in recommended_users_list}.values())
    
    context = {
        'users': users,
        'recommended_users': unique_recommended_users[:10], # 最大10人まで表示
    }
    return render(request, 'account/userlist.html', context)

#GETリクエストのみを受け付けるAPIビューであることを示す
#ログイン済みのユーザーだけがこのAPIにアクセスできる
#認証されていない場合は、自動的に403 Forbiddenエラーが返されます
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_info(request):
    """
    ログイン中のユーザー情報を返すAPIエンドポイント
    """
    # ユーザーが認証されている場合、その情報をJSONで返す
    return JsonResponse({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email
    })


# API用のUserListViewをここに追加
class UserListView(generics.ListAPIView):
    """
    全てのユーザーをリストするAPIビュー。
    フォロワー数でソートされます。
    """
    queryset = get_user_model().objects.all().annotate(followers_count=Count('followers')).order_by('-followers_count')
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

# API用のUserListViewをここに追加
class UserListView(generics.ListAPIView):
    """
    全てのユーザーをリストするAPIビュー。
    フォロワー数でソートされます。
    """
    queryset = get_user_model().objects.all().annotate(followers_count=Count('followers')).order_by('-followers_count')
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]


@login_required
def user_list_page(request):
    """
    user_list_page の中で「全ユーザー一覧」と
    「おすすめユーザー一覧」の両方から ブロック済みユーザーを除外 する必要あり
    最初に ブロック済みユーザーIDを取得 して、それを exclude() に追加
    """
    current_user = request.user

    # -------------------------------
    # 0. ブロック済みユーザーのIDを取得
    # -------------------------------
    blocked_ids = set(Block.objects.filter(blocker=current_user).values_list("blocked__id", flat=True))
    following_ids = set(Follow.objects.filter(follower=current_user).values_list('following__id', flat=True))

    # -------------------------------
    # 1. 全ユーザー（自分とブロック済みを除外）
    # -------------------------------
    users = (
        User.objects.exclude(id=current_user.id)   # 自分を除外
                    .exclude(id__in=blocked_ids)   # ブロック済みを除外
        .annotate(
            followers_count=Count('follower_set', distinct=True),
            following_count=Count('following_set', distinct=True),
        )
        .order_by('-followers_count')
        .prefetch_related(
            Prefetch(
                'tags',
                queryset=UserTag.objects.select_related('tag'),
                to_attr='prefetched_user_tags'
            )
        )
    )
    for u in users:
        u.is_following = u.id in following_ids
        u.is_blocked = u.id in blocked_ids

    # -------------------------------
    # 2. おすすめユーザー（ブロック済みを除外）
    # -------------------------------
    # 共通フォロー
    common_followers_ids = User.objects.filter(
        follower_set__following__in=following_ids
    ).exclude(
        Q(id=current_user.id) | Q(id__in=following_ids) | Q(id__in=blocked_ids)
    ).distinct().values_list('id', flat=True)

    # 共通タグ
    user_tags_ids = UserTag.objects.filter(user=current_user).values_list('tag__id', flat=True)
    common_tags_ids = User.objects.filter(
        tags__tag__in=user_tags_ids
    ).exclude(
        Q(id=current_user.id) | Q(id__in=following_ids) | Q(id__in=blocked_ids)
    ).distinct().values_list('id', flat=True)

    # ランダムユーザー
    exclude_ids = set(following_ids) | {current_user.id} | set(blocked_ids)
    all_others_ids = list(User.objects.exclude(id__in=exclude_ids).values_list('id', flat=True))
    random_users_ids = random.sample(all_others_ids, min(5, len(all_others_ids))) if all_others_ids else []

    # 重複排除
    recommended_user_ids = set(common_followers_ids) | set(common_tags_ids) | set(random_users_ids)

    # おすすめユーザー取得
    recommended_users = (
        User.objects.filter(id__in=recommended_user_ids)
        .annotate(
            followers_count=Count('follower_set', distinct=True),
            following_count=Count('following_set', distinct=True),
        )
        .prefetch_related(
            Prefetch(
                'tags',
                queryset=UserTag.objects.select_related('tag'),
                to_attr='prefetched_user_tags'
            )
        )
    )
    for u in recommended_users:
        u.is_following = u.id in following_ids
        u.is_blocked = u.id in blocked_ids

    context = {
        'users': users,  # ← 全ユーザーちゃんと表示
        'recommended_users': recommended_users[:10], 
    }
    return render(request, 'account/userlist.html', context)
