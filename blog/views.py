# blog/views.py

from profanity_filter.utils import check_for_profanity
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from comments.forms import CommentForm
from tags.models import Tag

def post_list(request):
    """
    ブログ投稿一覧を表示します。
    """
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    """
    個別のブログ投稿詳細を表示します。
    """
    post = get_object_or_404(Post, pk=pk)
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, object_id=post.pk, content_type=ContentType.objects.get_for_model(Post)).exists()
    form = CommentForm() # commentsアプリのフォームを使用
    return render(request, 'blog/post_detail.html', {'post': post, 'form': form, 'is_liked': is_liked})

@login_required
def post_new(request):
    """
    新しいブログ投稿を作成します。
    """
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data['content']
            if check_for_profanity(content):
                form.add_error('content', '不適切な言葉が含まれています。投稿内容を修正してください。')
            else:
                post = form.save(commit=False)  # <-- commit=False でインスタンス作成
                post.author = request.user      # <-- 著者を設定
                post.save()                     # <-- データベースに保存
                
                # タグを処理
                tags_str = form.cleaned_data.get("tags", "")
                tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
                
                # 投稿とタグの紐付け
                post.tags.clear() 
                for name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)
                
                return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'page_title': '新しい投稿'})

@login_required
def post_edit(request, pk):
    """
    既存のブログ投稿を編集します。
    """
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('blog:post_detail', pk=post.pk)
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            content = form.cleaned_data['content']
            if check_for_profanity(content):
                form.add_error('content', '不適切な言葉が含まれています。投稿内容を修正してください。')
            else:
                post = form.save(commit=False)
                post.author = request.user
                post.save()

                # タグを処理
                tags_str = form.cleaned_data.get("tags", "")
                tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
                
                post.tags.clear()
                for name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)

                return redirect('blog:post_detail', pk=post.pk)
    else:
        # フォームの初期値として既存のタグをカンマ区切りで表示
        tags_str = ", ".join([t.name for t in post.tags.all()])
        form = PostForm(instance=post, initial={'tags': tags_str})
    return render(request, 'blog/post_form.html', {'form': form, 'page_title': '投稿を編集'})

@login_required
def post_delete(request, pk):
    """
    ブログ投稿を削除します。
    """
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        post.delete()
    return redirect('blog:post_list')



@login_required
def post_like(request, pk):
    """
    ブログ投稿に「いいね」を付ける・解除するビュー。
    """
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        content_type = ContentType.objects.get_for_model(Post)
        like, created = Like.objects.get_or_create(
            user=request.user, 
            content_type=content_type, 
            object_id=post.pk
        )
        if not created:
            # 既にいいねが存在する場合は削除
            like.delete()
        # いいね処理後、投稿詳細ページにリダイレクト
    return redirect('blog:post_detail', pk=pk)