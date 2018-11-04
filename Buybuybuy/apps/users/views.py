from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import generics

from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU
from goods.serializers import SKUSerializer
from users.serializers import UserCreateSerializer, UserDetailSerializer, EmailSerializer, EmailActiveSerializer, \
    AddressSerializer, BrowseHistorySerializer
from .models import *
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import action

class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return Response({'username': username, 'count': count})


class MobileCountView(APIView):
    # 没有设计到模型类
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return Response({
            'mobile': mobile,
            'count': count
        })


class UserCreateView(CreateAPIView):
    # queryset = 当前进行创建操作，不需要查询
    serializer_class = UserCreateSerializer


class UserDetailView(generics.RetrieveAPIView):
    # queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    # 要求登录：
    permission_classes = [IsAuthenticated]

    # 视图中封装好的代码，是根据主键查询得到的对象
    # 需求：不根据pk查，而是获取登录的用户
    # 解决：重写get_object()方法
    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    '''保存用户邮箱'''
    permission_classes = [IsAuthenticated]
    # 修改当前登录用户的属性,所以不查询
    # queryset
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


class EmailActiveView(APIView):
    def get(self, request):
        # 接受数据并验证
        serializer = EmailActiveSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors)

        # 查询当前用户,并修改属性
        user = User.objects.get(Pk=serializer.validated_data.get('user_id'))
        user.email_active = True
        user.save()

        # 响应
        return Response({'message': 'OK'})


class AddressViewSet(ModelViewSet):
    # list======>>查询多个
    # create=====>>增加
    # retrieve==》根据主键查询1个，不需要
    # update===》修改
    # destroy==》删除
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.filter(is_delete=False)

    def list(self, request, *args, **kwargs):
        # 查询数据
        address_list = self.get_queryset()
        # 创建序列化器对象
        serializer = self.get_serializer(address_list, many=True)
        # 返回值的结构：
        '''
        {
            'user_id': 用户编号,
            'default_address_id': 默认收货地址编号,
            'limit': 每个用户的收货地址数量上限,
            'addresses': 地址数据，格式如[{地址的字典},{},...]
        }
        '''
        return Response({
            'user_id': self.request.user.id,
            'default_address_id': self.request.user.default_address_id,
            'limit': constans.ADDRESS_LIMIT,
            'addresses': serializer.data  # [{},{},...]
        })


    # destroy==》物理删除，重写，实现逻辑删除
    def destroy(self, request, *args, **kwargs):
        #根据主键查询对象
        address=self.get_object()

        #逻辑删除
        address.is_delete =True
        #保存
        address.save()
        #响应
        return Response(status=204)

        # 修改标题===>****/pk/title/------put
        # 如果没有detail=False=====>*****/title/
        # ^ ^addresses/(?P<pk>[^/.]+)/title/$ [name='addresses-title']
        # 设置收货地址的标题
        # 1不能够根据路由去写对应的视图,所以调用视图函数的action
    @action(methods=['put'],detail=True)
    def title(self,request,pk):
        #更据主键查询收货地址
        address=self.get_object()
        #接受数据,修改标题属性
        address.title=request.data.get('title')
        #保存
        address.save()
        #响应
        return Response({'title':address.title})

    #设置默认收货地址===>^ ^addresses/(?P<pk>[^/.]+)/status/$ [name='addresses-status']
    @action(methods=['put'],detail=True)
    def status(self,request,pk):
        #查找当前登录用户
        user=request.user
        #修改属性
        user.default_address_id=pk
        user.save()
        #响应
        return Response({'message':'OK'})

class BrowseHistoryView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    # serializer_class = BrowseHistorySerializer
    def get_serializer_class(self):
        # 创建与查询列表使用不同的序列化器
        if self.request.method == 'GET':
            return SKUSerializer
        else:
            return BrowseHistorySerializer

    # 查询需要指定查询集
    # queryset = SKU.objects.all()
    def get_queryset(self):
        # 连接redis
        redis_cli = get_redis_connection('history')
        # 查询当前登录用户的浏览记录[sku_id,sku_id,...]
        key = 'history_%d' % self.request.user.id
        sku_ids = redis_cli.lrange(key, 0, -1)
        # 遍历列表，根据sku_id查询商品对象
        skus = []
        for sku_id in sku_ids:
            skus.append(SKU.objects.get(pk=int(sku_id)))
        return skus  # [sku,sku,sku,...]

