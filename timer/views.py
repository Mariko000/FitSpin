from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import UserTimer
from .tasks import start_exercise_timer

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_timer(request):
    """
    ユーザーのタイマーを開始する
    """
    user = request.user

    # ① UserTimer が存在しなければ作る
    timer, created = UserTimer.objects.get_or_create(user=user)

    # ② タイマー情報を更新
    duration_minutes = request.data.get('duration', 10)  # 例: POST データで受け取る
    timer.end_time = timezone.now() + timezone.timedelta(minutes=duration_minutes)
    timer.notified = False  # 新しいタイマーなので通知済みフラグをリセット
    timer.save(update_fields=['end_time', 'notified'])

    # ③ Celery タスクを呼ぶ
    start_exercise_timer.delay(user.id)

    return JsonResponse({"status": "success", "end_time": timer.end_time.isoformat()})

@csrf_exempt
@login_required
def current_timer(request):
    """
    現在のタイマー情報を返す
    """
    try:
        timer = getattr(request.user, 'timer', None)
        if not timer or not timer.end_time:
            return JsonResponse({'end_time': None, 'notified': False})

        remaining = timer.end_time - timezone.now()
        return JsonResponse({
            'end_time': timer.end_time.isoformat(),
            'notified': getattr(timer, 'notified', False),
            'remaining_seconds': max(0, int(remaining.total_seconds()))
        })
    except Exception as e:
        # サーバー側での例外をログに残す
        print("current_timer error:", repr(e))
        return JsonResponse({'end_time': None, 'notified': False})