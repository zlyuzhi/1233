from django.shortcuts import render

# Create your views here.

from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserCreateSerializer
from .models import *



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
