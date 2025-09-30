# exercise/exercise/serializers.py
from rest_framework import serializers
from .models import Exercise

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'level'] # フロントエンドに渡したいフィールドを指定