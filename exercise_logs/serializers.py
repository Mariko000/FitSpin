# exercise_logs/serializers.py
from rest_framework import serializers
from .models import ExerciseLog
from tags.models import Tag

#保存用（POST用）・一覧取得（GET）
class ExerciseLogSerializer(serializers.ModelSerializer):
    # 書き込み用(tagsを文字列のリストで受け取る)
    tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    # 読み込み用(tagsを文字列のリストとして返す)
    tag_names = serializers.SerializerMethodField(read_only=True)

    # exercise はIDで受け取りつつ、読み込み時は名前も返す
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)

    class Meta:
        model = ExerciseLog
        fields = [
            'id', 'exercise', 'exercise_name',
            'date', 'time',
            'tags',          # POST用
            'tag_names',     # GET用
            'from_gacha',
        ]

    def get_tag_names(self, obj):
        return [t.name for t in obj.tags.all()]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        user = self.context['request'].user
        log = ExerciseLog.objects.create(user=user, **validated_data)

        # タグ保存
        for name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=name.strip())
            log.tags.add(tag)

        return log
