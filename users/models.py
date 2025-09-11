from django.urls import reverse
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Tag(models.Model):
    """
    ユーザーの興味を管理するためのタグモデル
    例: Python, Django, Vue.js
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Create your models here.
class User(AbstractUser):
    """
    ユーザー認証とプロフィールを拡張するカスタムユーザーモデル
    """

    email = models.EmailField(unique=True)  # メールをユニークにする

    avatar = models.ImageField(
        verbose_name='プロフィール画像',
        upload_to='profile_pictures/',
        null=True,
        blank=True,
    )
    
    # ImageSpecField を追加して、画像を自動的にリサイズ
    # ここで指定した `avatar_thumbnail` という属性で、リサイズされた画像にアクセス
    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(50, 50)], # 50x50ピクセルにリサイズ
        format='JPEG', # ファイル形式
        options={'quality': 60} # 画像の品質
    )

    bio = models.TextField(
        verbose_name='自己紹介',
        max_length=500,
        blank=True,
    )

    # 最終ログイン時間を保存するフィールド
    last_login_time = models.DateTimeField(null=True, blank=True)

    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'
        
    def __str__(self):
        return self.username
    
    def get_absolute_url(self):
        return reverse('users:user_profile_detail', args=[self.pk])

class LoginHistory(models.Model):
    """
    ユーザーのログイン履歴を記録するモデル
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    login_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'ログイン履歴'
        verbose_name_plural = 'ログイン履歴'
        ordering = ['-login_date']
        # 一日一回のログイン記録を保証
        unique_together = ('user', 'login_date')

    def __str__(self):
        return f"{self.user.username} logged in on {self.login_date}"
