# Fitspin/exercise/views.py
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Exercise
from .serializers import ExerciseSerializer
import random
import logging
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.views import update_login_streak
from users.views import update_login_streak, check_level_up


logger = logging.getLogger(__name__)


class BonusGachaExerciseView(APIView):
    """
    時間帯・曜日ボーナスを適用したガチャ（安全版）
    """   
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            update_login_streak(user)
        except Exception as e:
            logger.error(f"update_login_streak error: {e}")

        try:
            check_level_up(user)
        except Exception as e:
            logger.error(f"check_level_up error: {e}")

        current_level = getattr(user, 'status_level', 1)
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()

        try:
            # 基本は status_level に沿った運動
            base_qs = Exercise.objects.filter(level=current_level)

            # ボーナス運動
            lower_qs = Exercise.objects.filter(level=current_level - 1) if 6 <= hour < 9 and current_level > 1 else Exercise.objects.none()
            higher_qs = Exercise.objects.filter(level=current_level + 1) if weekday in (5,6) and current_level < 5 else Exercise.objects.none()
            night_qs = Exercise.objects.filter(level__in=[1,2]) if 20 <= hour < 23 else Exercise.objects.none()

            # プール作成
            pool = list(base_qs) + list(lower_qs) + list(higher_qs) + list(night_qs)

            # fallback: 万一プールが空なら基本レベルだけ
            if not pool:
                pool = list(base_qs)

            selected_exercise = random.choice(pool)

        except Exception as e:
            logger.error(f"Gacha selection error: {e}")
            selected_exercise = Exercise.objects.filter(level=current_level).first()
            if not selected_exercise:
                return Response({"detail": "運動データが存在しません。"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExerciseSerializer(selected_exercise)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PointBonusGachaExerciseView(APIView):
    """
    多分いま使っていない
    ポイント制＋時間帯・曜日ボーナスを統合したガチャ
    POST {"points_to_use": 1 or 3 or 5} で回せる
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            update_login_streak(user)
        except Exception as e:
            logger.error(f"update_login_streak error: {e}")

        try:
            check_level_up(user)
        except Exception as e:
            logger.error(f"check_level_up error: {e}")

        user.refresh_from_db()
        current_level = getattr(user, 'status_level', 1)

        try:
            points_to_use = int(request.data.get("points_to_use", 1))
        except Exception:
            points_to_use = 1

        if getattr(user, 'points', 0) < points_to_use:
            return Response({"detail": f"ポイント不足: {user.points}pt"}, status=status.HTTP_400_BAD_REQUEST)

        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()

        try:
            # 基本は status_level に沿った運動
            base_qs = Exercise.objects.filter(level=current_level, is_special=False)

            # ボーナス運動
            lower_qs = Exercise.objects.filter(level=current_level - 1, is_special=False) if 6 <= hour < 9 and current_level > 1 else Exercise.objects.none()
            higher_qs = Exercise.objects.filter(level=current_level + 1, is_special=False) if weekday in (5,6) and current_level < 5 else Exercise.objects.none()
            night_qs = Exercise.objects.filter(level__in=[1,2], is_special=False) if 20 <= hour < 23 else Exercise.objects.none()

            # プール作成
            pool = list(base_qs) + list(lower_qs) + list(higher_qs) + list(night_qs)

            # fallback
            if not pool:
                pool = list(base_qs)

            selected_exercise = random.choice(pool)

        except Exception as e:
            logger.error(f"Gacha selection error: {e}")
            selected_exercise = Exercise.objects.filter(level=current_level).first()
            if not selected_exercise:
                return Response({"detail": "運動データが存在しません。"}, status=status.HTTP_404_NOT_FOUND)

        # ポイント消費
        user.points = max(user.points - points_to_use, 0)
        user.save(update_fields=['points'])

        # 15pt以上でレベルアップ判定
        level_up_success = False
        if points_to_use >= 15:
            try:
                level_up_success = level_up_by_points(user, points_to_use=15)
                user.refresh_from_db()
            except Exception as e:
                logger.error(f"level_up_by_points error: {e}")

        serializer = ExerciseSerializer(selected_exercise)
        return Response({
            "exercise": serializer.data,
            "remaining_points": user.points,
            "level_up": level_up_success,
            "current_level": user.status_level
        }, status=status.HTTP_200_OK)

