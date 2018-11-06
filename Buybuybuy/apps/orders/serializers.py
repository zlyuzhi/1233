from datetime import datetime

from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from users.models import Address

'''
该怎么做
    生成一张订单,减少库存

问题是什么
    传过来的参数address pay_method怎么使用
    order_id 怎么返回


逻辑如下
1.创建订单对象
2.读取redis中选中的商品编号、数量
    2.1读hash中的商品、数量，转换成int
    2.2读set中选中的商品编号，转换成int
3.查询购物车中选中的商品对象
4.遍历
    4.1判断库存
    4.2修改商品的库存量、销量
    4.3创建订单商品对象
    4.4计算总数量、总金额
5.修改订单的总数量、总金额
6.删除redis中选中的商品

'''


class OrderCreateSerializer(serializers.Serializer):
    order_id = serializers.CharField(read_only=True)
    address = serializers.IntegerField(write_only=True)
    pay_method = serializers.IntegerField(write_only=True)

    # 验证
    def validate_address(self, value):
        count = Address.objects.filter(pk=value).count()
        if count <= 0:
            raise serializers.ValidationError('无效的收货地址')
        return value

    def validate_pay_method(self, value):
        if value not in [1, 2]:
            raise serializers.ValidationError('无效的付款方式')
        return value

    def create(self, validated_data):
        with transaction.atomic():
            sid =transaction.savepoint()
            # 获取验证的数据
            address = validated_data.get('address')
            pay_method = validated_data.get('pay_method')
            # 1.创建订单对象

            # 获取用户id
            user_id = self.context['request'].user.id
            # 生成主键
            order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%09d' % user_id
            total_count = 0
            total_amount = 0

            order = OrderInfo.objects.create(
                order_id=order_id,
                user_id=user_id,
                address_id=address,
                total_count=0,
                total_amount=0,
                freight=10,
                pay_method=pay_method
            )

            # 2.读取redis中选中的商品编号、数量
            redis_cli = get_redis_connection('cart')
            # 读书redis中的数据并且转换成int
            cart_redis = redis_cli.hgetall('cart_%d' % user_id)
            cart_dict = {}
            for sku_id, count in cart_redis.items():
                cart_dict[int(sku_id)] = int(count)
            sku_ids_redis = redis_cli.smembers('cart_selected_%d' % user_id)
            sku_ids = [int(sku_id) for sku_id in sku_ids_redis]

            # 查询购物车中选中的商品对象
            skus = SKU.objects.filter(pk__in=sku_ids)
            # 遍历
            for sku in skus:
                # 获取购买数量
                count = cart_dict[sku.id]

                # 判断库存
                if sku.stock < count:
                    #回滚
                    transaction.savepoint_rollback(sid)
                    raise serializers.ValidationError('库存不足')
                # 修改商品库存量,销量
                sku.stock -= count
                sku.sales += count
                sku.save()
                # 4.3创建订单商品对象
                OrderGoods.objects.create(
                    order_id=order_id,
                    sku_id=sku.id,
                    count=count,
                    price=sku.price
                )
                # 4.4 计算总数量,总金额
                total_count += count
                total_amount += count * sku.price

            # 5.修改订单的总数量、总金额
            order.total_count = total_count
            order.total_amount = total_amount
            order.save()
            # 提交事务si
            transaction.savepoint_commit(sid)

            # 6 删除redis中选中的商品
            redis_cli.hdel('cart_%d' % user_id, *sku_ids)
            redis_cli.srem('cart_selected_%d' % user_id, *sku_ids)

            #返回新建的订单对象
            return order
