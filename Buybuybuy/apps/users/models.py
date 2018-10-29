from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    email_active = models.BooleanField(default=False)


    class Meta:
        db_table = '手机号'
        verbose_name ='用户'
        verbose_name_plural=verbose_name
