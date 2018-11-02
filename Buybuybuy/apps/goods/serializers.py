from rest_framework import serializers

from goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    '''SKU序列化器'''
    class Meta:
       model=SKU
       fieldd=('id', 'name', 'price', 'default_image_url', 'comments')