from rest_framework import serializers

from ..models import Diary


class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['id', 'user', 'color', 'color_level', 'created_at', 'updated_at', 'context']