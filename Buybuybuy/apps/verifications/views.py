import random

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
# from Buybuybuy.celery_tasks.sms.tasks import send_sms_code
from Buybuybuy.apps.verifications import constants
from celery_tasks.sms.tasks import send_sms_code
# from Buybuybuy.utils.ytx_sdk.se

class SMSCodeView(APIView):
    #发送短信验证码
    def get(self,request,mobile):
        '''
        限制60秒内只向一个手机号码发送一次短信验证码
        '''
        # 获取redis的链接，从配置中cache处，根据名称获取连接
        redis_cli=get_redis_connection('sms_code')
        # 判断60秒以内是否发送过
        if  redis_cli.get('sms_flag_'+mobile):
        # 1 若已发送就提示已经发送
            raise serializers.ValidationError('向此手机号发短信太频繁了')
        # 2 若没有发送
        '''
        2.1 随机生成一个6位数的编码
        2.2 将编码保存到数据库（有保存时间的那种）
        3 返回什么（成功后的结果，API上的ok）
        '''
        # 2.1随机生成一个6位数的编码
        code =random.randint(100000,999999)
        print(code)
        # 2.2将编码保存到数据库（有保存时间的那种）验证码，发送的标记(还有多久)
        # 方法一
        # redis_cli.setex('sms_code'+mobile,constants.SMS_CODE_EXPIRES,code)
        # redis_cli.setex('sms_flag'+mobile,constants.SMS_FLAG_EXPIRES,1)
        # 方法二
        redis_pinpeline=redis_cli.pipeline()
        redis_pinpeline.setex('sms_code'+mobile,constants.SMS_CODE_EXPIRES,code)
        redis_pinpeline.setex('sms_flag'+mobile,constants.SMS_FLAG_EXPIRES,1)
        redis_pinpeline.execute()

        # 2.3发送短信：云通信
        # CCP.sendTemplateSMS(mobile,code,constants.SMS_CODE_EXPIRES/60,1)
        send_sms_code.delay(mobile, code, constants.SMS_CODE_EXPIRES / 60, 1)




        # 3 响应
        return Response({'message':'OK'})
