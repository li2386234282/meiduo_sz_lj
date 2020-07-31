import random

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
# from meiduo_mall.libs.captcha.captcha import captcha
#
# text,image = captcha.generate_captcha()
from django import http
from django.views.generic.base import View
from django_redis import get_redis_connection

from meiduo_mall.libs.captcha.captcha import Captcha
import logging
from celery_tasks.sms.tasks import ccp_send_sms_code

from meiduo_mall.libs.yuntongxun.ccp_sms import CCP

logger = logging.getLogger()

class ImageCodeView(View):
    def get(self,request,uuid):


        text,image =Captcha.generate_captcha()

        redis_conn = get_redis_connection("verify_code")

        redis_conn.setex('img_%s'%uuid,300,text)

        return HttpResponse(
            image,content_type="image/jpg"
        )


class SMSCodeView(View):
    def get(self,request,mobile):


        # 链接redis数据库:
        redis_conn = get_redis_connection('verify_code')
        # 从redis数据库中获取存入的数据
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 然后判断该数据是否存在, 因为上面的数据只存储60s,
        # 所以如果该数据存在, 则意味着, 不超过60s, 直接返回.
        if send_flag:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '发送短信过于频繁'})
        #接受参数
        image_code_client = request.GET.get('image_code')

        uuid = request.GET.get('image_code_id')

        #校验参数
        if not all([image_code_client,uuid]):
            return http.JsonResponse({
                'code':400,
                "errmsg":"缺少必传参数"
            },status=400)



        #创建连接到redis的对象
        redis_conn = get_redis_connection('verify_code')

        #提取图形验证码
        image_code_server= redis_conn.get('img_%s'%uuid)
        if image_code_client is None:

            #图形验证码不存在时的判定

            return http.JsonResponse({
                'code':400,
                "errmsg":"图形验证码失效"
            },status=400)

        #删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            logger.error(e)

        #对比图形验证码
        #bytes转字符串
        # image_code_client = image_code_server.decode()
        #转小写后比较
        if image_code_client.lower() != image_code_server.decode().lower():
            return http.JsonResponse({
                'code':400,
                'errmsg':"输入的验证码有误"
            })

        #随机生成六位数验证码
        sms_code = '%06d'%random.randint(0,999999)
        logger.info(sms_code)


        #保存有效时间为300秒的验证码
        redis_conn.setex('sms_%s'%mobile,300,sms_code)

        # 往redis中存入一个数据存储时间为60s
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)

        #创建管道
        pl = redis_conn.pipeline()

        # 按顺序执行
        # redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        pl.setex('sms_%s' % mobile, 300, sms_code)

        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)
        pl.setex('send_flag_%s' % mobile, 60, 1)

        #执行管道
        pl.execute()


        # CCP().send_template_sms(mobile,[sms_code,5],1)

        ccp_send_sms_code.delay(mobile,sms_code)

        #响应结果
        return http.JsonResponse({
            'code':0,
            'errmsg':"发送短信成功"
        })





