from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.serializers import UserCreateSerializer, UserDetailSerializer, EmailSerializer, EmailActiveSerializer, \
    AddressSerializer
from .models import *
from rest_framework.generics import UpdateAPIView


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
