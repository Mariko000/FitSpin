# Fitspin/exercise/urls.py
#Exercise専用のAPIエンドポイントだけなので、exercise/urls.pyに直接書いておく
#APIが増えてきたら exercise/api/urls.py を作って include する形に移行する
from django.urls import path
from .views import BonusGachaExerciseView, PointBonusGachaExerciseView

app_name = 'exercise'

urlpatterns = [
    path('bonus-gacha/', BonusGachaExerciseView.as_view(), name='shift-gacha'),
    path('point-bonus-gacha/', PointBonusGachaExerciseView.as_view(), name='point-gacha'),
]


