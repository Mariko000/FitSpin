from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from .models import LoginHistory
import datetime
from django.db.models.signals import post_save


@receiver(user_logged_in)
def create_login_history(request, user, **kwargs):
    """
    ユーザーがログインしたときにログイン履歴を記録します。
    """
    LoginHistory.objects.get_or_create(user=user, login_date=datetime.date.today())
