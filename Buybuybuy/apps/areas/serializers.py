from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name']


class AreaSubSubSerializer(serializers.ModelSerializer):
    # 关系属性，默认以pk输出，可以指定输出方式
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
