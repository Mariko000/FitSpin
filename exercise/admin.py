# backend/exercise/admin.py

from django.contrib import admin
from .models import Exercise



@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name','level')
    list_filter = ('level',) # レベルでフィルタできるようにする
    search_fields = ('name',)# 運動名と説明で検索できるようにする

    