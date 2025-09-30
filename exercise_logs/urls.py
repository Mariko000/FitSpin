# exercise_logs/urls.py
from django.urls import path
from .views import ExerciseLogCreateView, ExerciseLogListView, LatestExerciseLogView

urlpatterns = [
    path('', ExerciseLogCreateView.as_view(), name='exercise-log-create'),  # /exercise/api/logs/ にPOST
    path('list/', ExerciseLogListView.as_view(), name='exercise-log-list'), # /exercise/api/logs/list/ にGET
    path('latest/', LatestExerciseLogView.as_view(), name='exercise-log-latest'),  # GET最新1件
    path('logs/create/', ExerciseLogCreateView.as_view(), name='exercise_log_create'), #日付で絞るURL
]
