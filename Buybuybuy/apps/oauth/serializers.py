from rest_framework import serializers

from oauth import constants
from oauth.models import QQUser
from users.models import User
from utils import tjws


class QQBindSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField()
    sms_code = serializers.CharField()
    access_token = serializers.CharField()

    # 验证
    def validate(self, attrs):
        # 验证：短信验证码
        # 1.读取redis中的验证码
        # 2.读取请求中的验证码
        # 3.判断是否过期
        # 4.删除redis中验证码
        # 5.对比

        # 验证：access_token
        # 1 解密
        data_dict = tjws.loads(attrs.get('access_token'), constants.BIND_TOKEN_EXPIRES)
        # 2 判断是否过期
        if data_dict is None:
            raise serializers.ValidationError('access_token 过期')

        # 3 获取openid
        openid = data_dict.get('openid')

        # 4 加入字典
        attrs['openid'] = openid

        return attrs


    # 保存:创建
    def create(self, validated_data):
# validated_data 表示验证后的数据
        mobile =validated_data.get('mobile')
        openid=validated_data.get('openid')
        password =validated_data.get('password')

    #1 查询手机号是否对应一个用户
        try:
            user =User.objects.get(mobile=mobile)
        except:
            #如果没有对应着一个用户
            #创建用户
            user =User()
            user.username =mobile
            user.set_password(password)
            user.save()
        else:
            #如果对应着一个用户,进行密码对比
            #如果密码错误则跑出异常
             if not user.check_password(password):
                 raise  serializers.ValidationError('此手机号已被占用')

        # 绑定:创建QQUser对象
        qquser=QQUser()
        qquser.openid = openid
        qquser.user =user
        qquser.save()
        return qquser

