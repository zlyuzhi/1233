from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
from oauth import constants
from oauth.models import QQUser
from oauth.qq_sdk import OAuthQQ
from oauth.serializers import QQBindSerializer
from utils import tjws
from utils.jwt_token import generate


class QQurlView(APIView):
    def get(self, request):
        # 接受登录后的地址
        state = request.query_params.get('next')
        # 创建工具类对象
        oauthqq = OAuthQQ(state=state)
        # 获取授权地址
        url = oauthqq.get_qq_login_url()
        return Response({
            'login_url': url
        })


class QQLoginView(APIView):
    def get(self, request):
        # 获取code
        code = request.query_params.get('code')
        print(code)
        # 根据code获取token
        oauthqq = OAuthQQ()
        token = oauthqq.get_access_token(code)
        print(token)
        # 根据token 获取openid
        openid = oauthqq.get_openid(token)


        # 查询openid 是否存在
        try:
            qquser = QQUser.objects.get(openid=openid)
        except:
            # 如果不存在，则通知客户端转到绑定页面
            # 将openid加密进行输出
            data = tjws.dumps({'openid': openid}, constants.BIND_TOKEN_EXPIRES)
            # 响应
            return Response({
                'access_token': data
            })
        else:
            # 如果存在就状态保存,登录成功

            return Response({
                'user_id': qquser.user.id,
                'username':qquser.user.username,
                'token':generate(qquser.user)
            })


    def post(self,request):
        #接收
        serializer =QQBindSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message':serializer.errors
            })
        qquser =serializer.save()

        return Response({
            'user_id':qquser.user.id,
            'username':qquser.user.username,
            'token':generate(qquser.user)

        })