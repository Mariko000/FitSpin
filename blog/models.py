from django.db import models
from django.conf import settings # Djangoの設定ファイルにアクセスするためにインポート
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from tags.models import Tag

class Post(models.Model):
    """
    ブログ記事のモデル
    """
    title = models.CharField(max_length=200, verbose_name='タイトル')
    content = models.TextField(verbose_name='本文')
    body = models.TextField()
    image = models.ImageField(
        verbose_name='画像',
        upload_to='blog_images/',
        null=True,
        blank=True,
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='著者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    views = models.PositiveIntegerField(default=0, verbose_name='閲覧数')
    is_published = models.BooleanField(default=False)

    # GenericRelation を使用して comments アプリの Comment モデルと関連付け
    comments = GenericRelation('comments.Comment')
    # GenericRelationを使用して、PostモデルとLikeモデルを紐付ける
    likes = GenericRelation('likes.Like')

    # 追加: タグ（記事とタグの多対多）
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)


    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[str(self.pk)])

    class Meta:
        verbose_name = '投稿'
        verbose_name_plural = '投稿'
        ordering = ['-created_at'] # 新しい投稿が一番上に来るようにする