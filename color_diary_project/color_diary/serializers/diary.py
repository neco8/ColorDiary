from rest_framework import serializers

from ..models import Diary
from .color import ColorSerializer
from .user import UserSerializer


class DiarySerializer(serializers.ModelSerializer):
    color = ColorSerializer()
    user = UserSerializer()

    class Meta:
        model = Diary
        fields = ['id', 'color_level', 'created_at', 'updated_at', 'context']
        read_only_fields = ['user', 'color']