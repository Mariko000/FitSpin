#exercise_logs/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from tags.models import Tag

class ExerciseLog(models.Model):
    """
    運動ログをDBに保存するモデル

    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.ForeignKey('exercise.Exercise', on_delete=models.CASCADE)
    performed_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, blank=True)
    from_gacha = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.exercise.name} ({self.date} {self.time})"
