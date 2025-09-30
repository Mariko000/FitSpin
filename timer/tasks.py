from celery import shared_task
from pywebpush import webpush
from .models import UserTimer

@shared_task
def start_exercise_timer(user_id):
    timer = UserTimer.objects.get(user_id=user_id)
    subscription_info = timer.subscription_info  # JSON 形式で保存しておく
    payload = "タイマー終了！運動時間です！"

    webpush(
        subscription_info=subscription_info,
        data=payload,
        vapid_private_key="YOUR_PRIVATE_KEY",
        vapid_claims={"sub": "mailto:your@email.com"}
    )

    timer.notified = True
    timer.save(update_fields=['notified'])
