from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# Create your views here.
from carts.serializers import CartSerializer
from goods.models import SKU
from orders.serializers import OrderCreateSerializer


class CartListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        #1读取数据库中的数据
        redis_cli = get_redis_connection('cart')
        key_cart='cart_%d' %request.user.id

        key_selected='cart_selected_%d' %request.user.id
        cart_dict =redis_cli.hgetall(key_cart) # {sku_id:count,...}
        cart_selected =redis_cli.smembers(key_selected)# [sku_id,...]
        cart_dict2 ={}
        for sku_id,count in cart_dict.items():
            cart_dict2[int(sku_id)]=int(count)
        cart_selected2=[int(sku_id) for sku_id in cart_selected]

        # 2 查询商品对象
        skus =SKU.objects.filter(pk__in=cart_selected2)
        for sku in skus:
            sku.count =cart_dict2.get(sku.id)
            sku.selected =True
        # 3 序列化输出
        serializer=CartSerializer(skus,many=True)
        return Response({
            'freight':10,
            'skus':serializer.data
        })

class OrderCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer