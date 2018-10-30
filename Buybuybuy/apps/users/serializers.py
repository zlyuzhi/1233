import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_verify_mail
from users.models import User


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
        email=validated_data.get('email')
        instance.email=email
        instance.save()

        # 发送邮件,发出邮件即可给出提示，发的过程比较耗时,且不影响结果，可以在一个新进程中执行
        send_verify_mail.delay(email, instance.generate_verify_url())

        return instance

    #
    # def update(self, instance, validated_data):
    #     # 默认的里面有的方法(且不要写),因为需要向邮箱发送邮件,所以要重写修改方法
    #     # instance.email = validated_data.get('emil')
    #     # instance.save()
    #     email = validated_data.get('email')
    #     # 因为后面要单独使用Emily,所以独立出来,和原来没有变化
    #     instance.email = email
    #     instance.save()
    #
    #     # 发送激活邮件：发出邮件即可给出提示，发的过程比较耗时,且与结果没有任何关系，可以在一个新进程中执行
    #     send_verify_mail.delay(email, instance.generate_verify_url())
    #     return instance

