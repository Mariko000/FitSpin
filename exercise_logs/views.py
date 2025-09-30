# exercise_logs/views.py
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ExerciseLog
from .serializers import ExerciseLogSerializer

# exercise_logs/views.py
class ExerciseLogCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExerciseLogSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            # 受信データに gacha 情報があれば判定（真偽判定を厳密に）
            raw = request.data.get('from_gacha', False)
            from_gacha = str(raw).lower() in ('1', 'true', 'yes')

            log = serializer.save()  # 通常の保存

            # 万が一 serializer が from_gacha を保存していなければ補正
            if from_gacha and not getattr(log, 'from_gacha', False):
                log.from_gacha = True
                log.save(update_fields=['from_gacha'])

            # ポイント付与など既存処理
            request.user.add_points(2)

            # *** ここが重要: セッションにガチャ完了フラグを立てる（１回だけ使う） ***
            if from_gacha:
                request.session['gacha_completed'] = True
                request.session.modified = True

            return Response({
                "exercise_log": ExerciseLogSerializer(log).data,
                "points": request.user.points
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#ユーザー全履歴  *週間進捗や日別履歴に必要
class ExerciseLogListView(ListAPIView):
    serializer_class = ExerciseLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExerciseLog.objects.filter(user=self.request.user).order_by('-date', '-time')
    
class ExerciseLogByDateView(ListAPIView):
    serializer_class = ExerciseLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        date = self.kwargs['date']  # yyyy-mm-dd 形式
        return ExerciseLog.objects.filter(user=self.request.user, date=date).order_by('-time')

# 既存ログから最新1件を取得して返すだけのビュー
class LatestExerciseLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest_log = ExerciseLog.objects.filter(user=request.user).order_by('-created_at').first()
        if not latest_log:
            return Response({"detail": "No logs found."}, status=404)
        serializer = ExerciseLogSerializer(latest_log)
        return Response(serializer.data)
