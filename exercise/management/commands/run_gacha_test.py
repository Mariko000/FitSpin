import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from exercise.models import Exercise
from exercise.views import BonusGachaExerciseView, PointBonusGachaExerciseView

class Command(BaseCommand):
    help = "ガチャ・CSV取り込み・ボーナスロジックの動作確認をまとめて実行"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== CSVデータ確認 ==="))
        special_count = Exercise.objects.filter(is_special=True).count()
        self.stdout.write(f"スペシャル運動の件数: {special_count}")

        level3_list = Exercise.objects.filter(level=3)
        self.stdout.write(f"レベル3の運動一覧: {[e.name for e in level3_list]}")

        self.stdout.write(self.style.NOTICE("=== 基本ガチャ（時間帯・曜日ボーナス）確認 ==="))
        factory = APIRequestFactory()
        view = BonusGachaExerciseView.as_view()
        request = factory.get('/exercise/bonus-gacha/')
        User = get_user_model()
        request.user = User.objects.first()
        response = view(request)
        self.stdout.write(f"基本ガチャの結果: {response.data}")

        self.stdout.write(self.style.NOTICE("=== ポイント制ガチャ確認 ==="))
        user = User.objects.first()
        user.points = 10
        user.save()
        factory = APIRequestFactory()
        view = PointBonusGachaExerciseView.as_view()
        request = factory.post('/exercise/point-bonus-gacha/', {'points_to_use': 5})
        request.user = user
        response = view(request)
        self.stdout.write(f"ポイント制ガチャ結果: {response.data}")

        self.stdout.write(self.style.NOTICE("=== ボーナス確率調整例 ==="))
        # 基本プールと軽めプールがある場合の例
        base_qs = Exercise.objects.filter(level=user.status_level)
        lower_qs = Exercise.objects.filter(level=max(user.status_level-1, 1))
        pool = list(base_qs) * 8 + list(lower_qs) * 2
        selected = random.choice(pool)
        self.stdout.write(f"調整プールから選ばれた運動: {selected}")
