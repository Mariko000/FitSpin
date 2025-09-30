from django.contrib import admin
from .models import ExerciseLog

@admin.register(ExerciseLog)
class ExerciseLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'date', 'time')

    def date(self, obj):
        return obj.performed_at.date()

    def time(self, obj):
        return obj.performed_at.time()
