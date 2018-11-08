from alipay import AliPay
from django.conf import settings
from django.shortcuts import render


# Create your views here.
from rest_framework.response import Response

from rest_framework.views import APIView

from orders.models import OrderInfo


class AliPayURLView(APIView):
    def get(self, request, order_id):
        try:
            order = OrderInfo.objects.get(pk=order_id)
        except:
            raise Exception('订单编号无效')

        # 2创建alipay对象(参考文档)
        alipay = AliPay(
            # appid='setting.ALIPAY_APPID',
            appid='2016092000553693',
            app_notify_url=None,

            app_private_key_path=settings.ALIPAY_PRIVATE_KEY_PATH,

            alipay_public_key_path=settings.ALIPAY_PUBLIC_KEY_PATH,

            debug=settings.ALIPAY_DEBUG
        )
        order_string = alipay.api_alipay_trade_page_pay(
            subject=settings.ALIPAY_SUBJECT,
            out_trade_no=order_id,  # 订单编号
            total_amount=str(order.total_amount),  # 支付总金额，类型为Decimal(),不支持序列化，需要强转成str
            return_url=settings.ALIPAY_RETURN_URL

        )

        # 返回url
        return Response({'alipay_url': settings.ALIPAY_GATE + order_string})


class OrderStatusView(APIView):
    def put(self,request):
        alipay_dict =request.query_params.dict()