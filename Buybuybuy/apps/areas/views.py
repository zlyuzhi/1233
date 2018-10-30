from django.shortcuts import render
from rest_framework.generics import *
# Create your views here.
# 查多个list：返回所有的省信息
# 查一个retrieve：返回pk对应的地区，并包含它的子级地区
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area
from areas.serializers import AreaSerializer, AreaSubSubSerializer


# class AreaListView(ListAPIView):
#     queryset = Area.objects.filter(parent__isnull=True)
#     serializer_class = AreaSerializer
#
#
# class AreaRetrieveView(RetrieveAPIView):
#     queryset = Area.objects.all()
#     serializer_class = AreaSubSubSerializer

class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    # action:指定请求方式与处理函数的对应关系
    # list===>get
    # retrieve==>get
    # queryset =
    # serializer_class =
    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent__isnull=True)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action=='list':
            return AreaSerializer
        else:
            return AreaSubSubSerializer
