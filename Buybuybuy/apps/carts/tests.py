from django.http import request
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection

from rest_framework.response import Response
from rest_framework.views import APIView

from carts import serializers, contants
from goods.models import SKU
from utils import myjson


class CartView(APIView):
    def user(self, request):
        try:
            user = request.user
        except:
            user = None
        return user

    def read_cookie(self, request):
        # 获取cookie中购物车信息
        cart_str = request.COOKIES.get('cart')
        cart_dict = myjson.loads(cart_str)
        return cart_dict

    def perform_authentication(self, request):
        # 在执行视图函数前,不进行身份检查
        pass

    def post(self, request):
        # 判定用户是否登录
        try:
            # 如果用户认证信息不存在就抛出异常
            user = request.user
        except:
            user = None

        #  接受请求数据,进行验证
        serializer = serializers.CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 验证后获取数据,便于后面的一系列操作
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']

        # 构造响应对象
        response = Response(serializer.validated_data)

        if user is None:
            # 如果用户未登录,则存入cookie
            # 读取cookies中的数据
            #:返回sku_id,count,select,
            # 从cookies(以前可能写进去过)取出数据,把他转换成字典
            # 取出count,如果已经存在,则再加进去

            cart_str = request.COOKIES.get('cart')
            if cart_str is None:
                cart_dict = {}
            else:
                cart_dict = myjson.loads(cart_str)
            # 取出原数量
            if sku_id in cart_dict:
                count_cart = cart_dict[sku_id]['count']
            else:
                count_cart = 0
            # 修改数据
            cart_dict[sku_id] = {

                'count': count + count_cart,
                'selected': True
            }

            # 写cookie
            cart_str = myjson.dumps(cart_dict)
            response.set_cookie('cart', cart_str, max_age=contants.CART_COOKIE_EXPIRES)
        else:
            # 如果已经登录,存入redis
            # 连接redis
            redis_cli = get_redis_connection('cart')
            # 构造键，因为服务器会存多个用户的购物车信息，通过用户编号可以区分
            key = 'cart_%d' % request.user.id
            key_select = 'cart_selected_%d' % request.user.id

            redis_cli.hset(key, sku_id, count)
            redis_cli.sadd(key_select, sku_id)

        return response

    # 展示购物车
    def get(self, request):
        user = self.user(request)
        # try:
        #     user = request.user
        # except:
        #     user = None
        # return user

        if user is None:
            # 未登录,读取cookie
            # cart_dict = self.read_cookie(request)

            cart_str = request.COOKIES.get('cart')
            cart_dict = myjson.loads(cart_str)
            # 根据商品编号查询对象,并添加数量,属性
            skus = []
            for key, value in cart_dict.items():
                sku = SKU.objects.get(pk=key)
                sku.count = value['count']
                sku.selected = value['selected']
                skus.append(sku)
        else:
            # 已登录,读取redis
            # 连接redis
            redis_cli = get_redis_connection('cart')
            # 构造键，因为服务器会存多个用户的购物车信息，通过用户编号可以区分
            key = 'cart_%d' % request.user.id
            key_select = 'cart_selected_%d' % request.user.id
            # 从hash中读取个人所有商品编号
            sku_ids = redis_cli.hkeys(key)
            # 读取选中的商品编号
            sku_ids_selected = redis_cli.smembers(key_select)
            sku_ids_selected = [int(sku_id) for sku_id in sku_ids_selected]

            # 查询商品
            skus = SKU.objects.filter(pk__in=sku_ids)

            # 遍历商品，增加数量、选中属性
            for sku in skus:
                sku.count = redis_cli.hget(key, sku.id)
                sku.selected = sku.id in sku_ids_selected

        # 序列化输出
        serializer = serializers.CartSerializer(skus, many=True)
        return Response(serializer.data)

    def put(self, request):
        user = self.user(request)
        # 接受数据并验证数据
        serializer = serializers.CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 验证通过后修改数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        response = Response(serializer.validated_data)

        if user is None:
            # 读取cookie里面的值
            cart_str = request.COOKIES.get('cart')
            cart_dict = myjson.loads(cart_str)
            # 修改
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 3 保存
            cart_str = myjson.dumps(cart_dict)
            response.set_cookie('cart', cart_str, max_age=contants.CART_COOKIE_EXPIRES)
        else:
            #  已登录
            # 连接redis
            redis_cli = get_redis_connection('cart')
            # 构造键，因为服务器会存多个用户的购物车信息，通过用户编号可以区分
            key = 'cart_%d' % request.user.id
            key_select = 'cart_selected_%d' % request.user.id
            # 修改数量
            redis_cli.hset(key, sku_id, count)
            # 修改选中
            if selected:
                redis_cli.sadd(key_select, sku_id)
            else:
                redis_cli.srem(key_select, sku_id)

        return response
