from rest_framework import serializers

from ..models import Color


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'hex_color']

    def to_representation(self, instance):
        '''
        split hex_color into code and alpha.
        #FFF000-1.0 -> {'hex_color_code': 'FFF000', 'alpha': 1.0}
        '''
        ret = super().to_representation(instance)
        ret['hex_color'] = {
            'code': str(ret['hex_color']).split('-')[0],
            'alpha': float(str(ret['hex_color']).split('-')[1])
        }
        return ret