from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from users import constans
from utils import tjws


class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    email_active = models.BooleanField(default=False)


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
