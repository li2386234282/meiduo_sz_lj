import re,json


from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from QQLoginTool.QQtool import OAuthQQ
from django.views import View
from .models import OAuthQQUser
from itsdangerous import TimedJSONWebSignatureSerializer


class QQFirstView(View):
    def get(self,request):

        #next表示从哪个页面进入到的登录页面
        #将来登录成功后就自动回到哪个页面
        next = request.GET.get('next')

        #获取qq登录页面的网址
        #创建OAuthQQ类的对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                    client_secret=settings.QQ_CLIENT_SECRET,
                    redirect_uri=settings.QQ_REDIRECT_URI,
                    state=next)

        #调用对象的获取qq地址方法
        login_url = oauth.get_qq_url()


        #返回登录地址
        return JsonResponse({
            'code':0,
            'errmsg':'ok',
            'login_url':login_url
        })


def generate_access_token(openid):
    #功能：解密出openid
    #参数：openid用户的qq标示
    #返回token值
    serializer = TimedJSONWebSignatureSerializer(
        secret_key=settings.SECRET_KEY,
        expires_in=3600*24*14#定义当前生成的token的有效期为14天
    )
    #加密的数据是一个字典
    data = {'openid':openid}

    access_token = serializer.dumps(data)

    return access_token.decode()


class QQUserView(View):
    # 第二个端口的实现
    def get(self,request):

        #获取从前段发送来的code参数
        code = request.GET.get("code")

        #验证code获取token
        try:
            oauth_qq = OAuthQQ(
                client_id=settings.QQ_CLIENT_ID,
                client_secret=settings.QQ_CLIENT_SECRET,
                redirect_uri=settings.QQ_REDIRECT_URI
            )
            token = oauth_qq.get_access_token(code)

            #根据token获取openid
            openid = oauth_qq.get_open_id(access_token=token)
        except Exception as e:
            print(e)
            return JsonResponse({
                "code":400,
                'errmsg':"qq登录失败！"
            })
        try:
            oauth_qq = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist as e:
            #用户没有绑定过qq,我们需要返回加密的openid
            access_token = generate_access_token(openid)
            return JsonResponse({
                'access_token': access_token
            })

        #用户已经绑定过qq-->登录成功
        user = oauth_qq.user
        #状态保持
        login(request,user)
        response = JsonResponse({'code':0,'errmsg':"ok"})
        response.set_cookie("username",user.username,max_age=3600*24*14)
        return response
