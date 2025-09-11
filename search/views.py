from django.shortcuts import render
# views.py（例）
from django.db.models import Q
from blog.models import Post
from django.contrib.auth import get_user_model
from tags.models import Tag, UserTag

User = get_user_model()

@login_required
def search_view(request):
    query = request.GET.get("q", "")
    results = {
        "blog_posts": [],
        "users": [],
        "tags": [],
        "users_with_tag": []
    }

    if query:
        # ブログ投稿
        results["blog_posts"] = Post.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        ).select_related("author").prefetch_related("tags")

        # ユーザー
        results["users"] = User.objects.filter(
            Q(username__icontains=query) | Q(bio__icontains=query)
        )

        # タグ
        results["tags"] = Tag.objects.filter(name__icontains=query)

        # そのタグを持つユーザー
        results["users_with_tag"] = User.objects.filter(
            tags__tag__name__icontains=query
        ).distinct()

    return render(
        request,
        "search_results.html",
        {"query": query, "results": results}
    )


# Create your views here.
