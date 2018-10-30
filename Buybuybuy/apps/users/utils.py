import re

from django.contrib.auth.backends import ModelBackend

from users.models import User



def jwt_response_payload_handler(token, user=None, request=None):
    '''
    自定义jwt认证成功返回数据
    '''
    print(token)
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_count(account):
    '''
    根据账号获取user对象
    :param account: 账号,可以是用户名,也可以是手机号
    :return:User对象或者None
    '''
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # 账号为手机号
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)

    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户名或者手机号认证"""
    def authenticate(self,request,username=None,password=None,**kwargs):
        user =get_user_by_count(username)
        if user is not None and user.check_password(password):
            return user



# from django.contrib.auth.backends import ModelBackend
# from .models import User
# import re
#
#
# def jwt_response_payload_handler(token, user=None, request=None):
#     return {
#         'token': token,
#         'user_id': user.id,
#         'username': user.username
#     }
#
#
# class MyModelBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             # 判断username是用户名，还是手机号
#             if re.match(r'^1[3-9]\d{9}$', username):
#                 # 手机号
#                 user = User.objects.get(mobile=username)
#             else:
#                 # 用户名
#                 user = User.objects.get(username=username)
#         except:
#             return None
#
#         # 判断密码
#         if user.check_password(password):
#             return user
#         else:
#             return None
#
#             # 返回user对象