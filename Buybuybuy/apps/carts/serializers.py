from rest_framework import serializers

from goods.models import SKU


class CartAddSerializer(serializers.Serializer):
    sku_id=serializers.IntegerField()
    count=serializers.IntegerField(min_value=1)
    selected =serializers.BooleanField(default=True)

    def validate_sku_id(self,value):
        #前段有这个请求参数sku_id
        count =SKU.objects.filter(pk=value).count()
        if count <= 0:
            raise serializers.ValidationError('无效的商品编号')
        return value


class CartSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    selected = serializers.BooleanField()

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'count', 'selected']
