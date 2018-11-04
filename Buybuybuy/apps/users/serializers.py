import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from goods.models import SKU
from users import constans
from users.models import User, Address
from celery_tasks.email.tasks import send_verify_mail
from utils import tjws


class UserCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)  # 不接收客户端的数据，只向客户端输出
    token = serializers.CharField(read_only=True)
    username = serializers.CharField(min_length=5, max_length=20, error_messages=({
        'min_length': '用户名字长度不够(5-20)',
        'max_length': '用户名过长(5-20)'
    }))
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    sms_code = serializers.CharField(write_only=True)
    mobile = serializers.CharField()
    allow = serializers.BooleanField(write_only=True)

    # 验证
    # 1 验证用户名
    def validate(self, attrs):
        # print(attrs)
        if User.objects.filter(username=attrs.get('username')).count():
            raise serializers.ValidationError('用户名已经存在')

        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        # 验证短信验证码
        # 一个从获取的,一个从数据路redis来的
        sms_code_quest = attrs.get('sms_code')
        mobile = attrs.get('mobile')
        # print(mobile)
        redis_cli = get_redis_connection('sms_code')
        sms_code_redis = redis_cli.get('sms_code' + mobile)
        # print(sms_code_redis)
        # 先判断是否过期
        if not sms_code_redis:
            raise serializers.ValidationError('短信验证码过期')
        # 强制删除
        redis_cli.delete('sms_code' + mobile)
        # 换成整型
        if int(sms_code_redis) != int(sms_code_quest):
            raise serializers.ValidationError('验证码不一致')

        # 验证手机
        # 1验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', attrs.get('mobile')):
            raise serializers.ValidationError('手机格式错误')
        # 2 验证是否重复
        count = User.objects.filter(mobile=attrs.get('mobile')).count()
        if count > 0:
            raise serializers.ValidationError('手机已经被注册')

        if not attrs.get('allow'):
            raise serializers.ValidationError('请同意协议')

        return attrs

    # 保存数据
    def create(self, validated_data):
        user = User()
        user.username = validated_data.get('username')
        user.set_password(validated_data.get('password'))
        user.mobile = validated_data.get('mobile')
        user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)  # header.payload.signature

        # 将token输出到客户端
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']


class EmailSerializer(serializers.ModelSerializer):
    # 用模型类里面有的属性就用Modelserializer
    class Meta:
        model = User
        fields = ['email']

    # 重写修改方法，在修改属性后，需要向邮箱发送邮件
    def update(self, instance, validated_data):
        email = validated_data.get('email')
        instance.email = email
        instance.save()

        # 发送邮件,发出邮件即可给出提示，发的过程比较耗时,且不影响结果，可以在一个新进程中执行
        send_verify_mail.delay(email, instance.generate_verify_url())

        return instance


class EmailActiveSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=200)

    def validate(self, attrs):
        # 获取加密字符串
        token = attrs.get('token')
        # 解密
        data_dict = tjws.loads(token, constans.VERIFY_EMAIL_EXPIRES)
        # 判断是否过期
        if data_dict is None:
            raise serializers.ValidationError('激活链接已经过期')
        attrs['user_id'] = data_dict.get('user_id')
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    # 关系属性,使用id接受,不然接受的是个对象,所以要用单独接受
    province_id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    district_id = serializers.IntegerField()
    # 关系属性,改成你字符串输出
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    # 重写创建,因为视图函数的创建是在这里写的
    def create(self, validated_data):
        # 默认的实现中,没有指定属性User,则添加时必然会报错,所以需要指定User属性
        # 现在问题是如何在序列化器中找到user,找request,
        # user对象不是客户端传过来的
        validated_data['user'] = self.context['request'].user
        address = super().create(validated_data)

        # address=Address.objects.create(validated_data)
        return address

    class Meta:
        model = Address
        # 拍粗不必要的字段,用户不需要传递,设为当前用户
        exclude = ['is_delete', 'create_time', 'update_time', 'user']


class BrowseHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    def validate_sku_id(self, value):
        # 查询商品编号是否存在
        count = SKU.objects.filter(pk=value).count()
        if count <= 0:
            raise serializers.ValidationError('商品编号无效')
        return value

    def create(self, validated_data):
        sku_id = validated_data['sku_id']
        # 连接redis
        redis_cli = get_redis_connection('history')
        # 根据不同的用户构造键
        key = 'history_%d' % self.context['request'].user.id
        # 1.删除sku_id
        redis_cli.lrem(key, 0, sku_id)
        # 2.添加
        redis_cli.lpush(key, sku_id)
        # 3.判断长度
        if redis_cli.llen(key) > constans.BROWSE_HISTORY_LIMT:
            # 4.如果超过长度则删除最后一个
            redis_cli.rpop(key)

        return {'sku_id': sku_id}