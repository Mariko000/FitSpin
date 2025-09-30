from django.db import models
from django.utils import timezone
from django.conf import settings

class Timer(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notified = models.BooleanField(default=False)
    subscription_info = models.JSONField()  # ブラウザの push subscription を保存
    


# ユーザーごとのタイマー状態を管理するモデル
class UserTimer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # settings.AUTH_USER_MODEL を使う
        on_delete=models.CASCADE,
        related_name='timer'
    )
    end_time = models.DateTimeField(null=True, blank=True)
    subscription_info = models.JSONField(null=True, blank=True)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Timer"