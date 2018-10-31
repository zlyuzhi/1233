from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from users import constans
from utils import tjws
from utils.models import BaseModel


class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    email_active = models.BooleanField(default=False)
    default_address =models.OneToOneField('users.Address',related_name='user_addr', null=True, blank=True)

    class Meta:
        db_table = '手机号'
        verbose_name ='用户'
        verbose_name_plural=verbose_name

    def generate_verify_url(self):
        # 构造有效数据
        data = {'user_id': self.id}
        # 加密
        token = tjws.dumps(data, constans.VERIFY_EMAIL_EXPIRES)
        # 构造激活链接
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token

class Address(BaseModel):
    #所属用户
    user =models.ForeignKey(User,related_name='addresses')
    #名称
    title = models.CharField(max_length=20)
    #收件人
    receiver=models.CharField(max_length=10)
    #省
    province=models.ForeignKey('areas.Area',related_name='province_address')
    #市
    city= models.ForeignKey('areas.Area',related_name='city_address')
    # 区
    district=models.ForeignKey('areas.Area',related_name='distict_address')
    # 详细地址
    place =models.CharField(max_length=100)
    #手机
    mobile=models.CharField(max_length=11)
    #固定电话
    tel =models.CharField(max_length=20,null=True,blank=True)
    #邮箱
    emile=models.CharField(max_length=50,null=True,blank=True)
    #逻辑删除
    is_delete =models.BooleanField(default=False)

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
