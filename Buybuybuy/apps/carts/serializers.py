from rest_framework import serializers

from goods.models import SKU


class CartAddSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField()
    count = serializers.IntegerField(min_value=1)
    # stock = serializers.IntegerField()
    selected = serializers.BooleanField(default=True, required=False)

    def validate_sku_id(self, value):
        # 前段有这个请求参数sku_id
        count = SKU.objects.filter(pk=value).count()
        if count <= 0:
            raise serializers.ValidationError('无效的商品编号')
        return value

    # def validate_stock(self,value):
    #     stock=SKU.objects.filter(pk=value).stock
    #     if stock<0:
    #         raise serializers.ValidationError('没有东西了')
    #     return value

class CartSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    selected = serializers.BooleanField()

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'count', 'selected']


class CartDeleteserializer(serializers.Serializer):
    sku_id = serializers.IntegerField()

    def validate_sku_id(self, value):
        count = SKU.objects.filter(pk=value).count()
        if count <= 0:
            raise serializers.ValidationError('商品不存在')
        return value


class CartSelectSerializer(serializers.Serializer):
    selected = serializers.BooleanField()
