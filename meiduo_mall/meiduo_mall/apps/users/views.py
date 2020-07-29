import json

from django import http
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection

from users.models import User
import re
from django.contrib.auth import login, authenticate


# Create your views here.

class UsernameCountView(View):
    def get(self,request,username):
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            print(e)
            return JsonResponse({
                "code": 400,
                "errmsg": "查询数据出错",
            })

        return JsonResponse({
            "code": 0,
            "errmsg": "ok",
            "count": count,
        })

class MobileCountView(View):
    def get(self,request,mobile):

        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            print(e)
            return JsonResponse({
                "code":400,
                "errmsg":"查询数据出错",
            })

        return JsonResponse({
            "code":0,
            "errmsg":"ok",
            "count":count,


        })

#用户注册接口定义
class RegisterView(View):
    def post(self,request):
        #接收参数
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        password2 = dict.get('password2')
        mobile = dict.get('mobile')
        allow = dict.get('allow')
        sms_code_client = dict.get('sms_code')

        #整体校验
        if not all([username,password,password2,mobile,allow,sms_code_client]):
            return  http.JsonResponse({
                'code':400,
                "errmsg":"缺少必传参数"
            })

        #用户名校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'username格式有误'})

        #密码校验
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'password格式有误'})

        #二次输入密码校验
        if password != password2:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '两次输入不对'})

        #mobile校验
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'mobile格式有误'})

        #allow校验
        if allow != True:
            return http.JsonResponse({'code': 400,
                                      'errmsg': 'allow格式有误'})

        #sms_code校验(链接redis数据库)
        redis_conn = get_redis_connection('verify_code')

        #从redis中取值
        sms_code_server = redis_conn.get('sms_%s' % mobile)


        #判断该值是否存在
        if not sms_code_server:
            return http.JsonResponse({
                'code':400,
                "errmsg":"短信验证码过期"
            })

        #判断验证码与发送的验证码是否一样
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({
                'code':400,
                'errmsg':"验证码有误"
            })

        #保存到数据库捕获异常
        try:
            user = User.objects.create(username=username,password=password,mobile=mobile)

        except Exception as e:
            return http.JsonResponse({
                'code':400,
                'errmsg':"保存到数据库出错"
            })

        #状态保持


        login(request,user)

        #拼接json返回
        response = JsonResponse({
            'code':0,
            "errmsg":"ok"
        })

        response.set_cookie(
            'username',
            username,
            max_age=3600*24*14
        )
        return response

#用户登录接口
class LoginView(View):
    def post(self,request):
        #接受参数
        dict = json.loads(request.body.decode())
        username = dict.get('username')
        password = dict.get('password')
        remembered = dict.get('remembered')


        #校验
        if not all([username,password]):
            return JsonResponse({
                'code':400,
                "errmsg":'缺少必传参数'
            })
        if not re.match(r'^\w{5,20}$', username):
            return JsonResponse({'code':400, 'errmsg': '用户名格式有误'}, status=400)

        if not re.match(r'^\w{8,20}$', password):
            return JsonResponse({'code':400, 'errmsg': '密码格式有误'}, status=400)

        #验证是否能够登录
        # user = authenticate(request,username=username,
        #                     password=password)
        # if user is None:
        #     return JsonResponse({
        #         'code':400,
        #         'errmsg':'用户名或密码错误'
        #
        #     })
        # #状态保持
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            return JsonResponse({'code': 400, 'errmsg': '用户名错误！'})
        if not user.check_password(password):
            return JsonResponse({'code': 400, 'errmsg': '密码错误！'})
        # if not user:
        #     return JsonResponse({"code": 400, 'errmsg': '您提供的身份信息无法验证！'}, status=401)

        login(request,user)

        #判断是否记住密码
        if remembered != True:
            request.session.set_expiry(0)

        else:
            request.session.set_expiry(None)

        #返回Json
        return JsonResponse({
            'code':0,
            'errmsg':'ok'
        })

        #构建响应

        response = JsonResponse({'code': 0, 'errmsg': 'ok'})

        response.set_cookie(
            'username',
            username,
            max_age=3600 * 24 * 14
        )

        return response













