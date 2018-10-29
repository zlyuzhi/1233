from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserCreateSerializer, UserDetailSerializer, EmailSerializer
from .models import *
from  rest_framework.generics import UpdateAPIView



class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return Response({'username': username, 'count': count})


class MobileCountView(APIView):
#没有设计到模型类
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
    #修改当前登录用户的属性,所以不查询
    #queryset
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user
