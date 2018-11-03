from django.shortcuts import render

# Create your views here.
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.generics import ListAPIView

from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer
from utils.pagination import SKUListPagination
from rest_framework.filters import OrderingFilter


class SKUListView(ListAPIView):
    #queryset=SKU.object.all()
    def get_queryset(self):
        #查询多个时,获取路径中的参数:self.kwargs====>字典
        return SKU.objects.filter(category_id=self.kwargs['category_id'])

    serializer_class = SKUSerializer

    #分页

    pagination_class = SKUListPagination
    #排序
    # 1 去setting里面注册
    # 2 指定排序的类OrderingFilter
    filter_backends = [OrderingFilter]
    #3 指定按照什么循序(字段)来排
    OrderingFilter=['create_time', 'price', 'sales']


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    # 模型类可改
    index_models = [SKU]
    # 序列化器
    serializer_class = SKUIndexSerializer
    # 分页
    pagination_class = SKUListPagination
