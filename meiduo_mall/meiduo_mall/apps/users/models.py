from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


# 由于以下2点，所以我们需要自定义用户模型类，并继承Django点抽象用户基类
# 1、Django默认用户模型类中没哟mobile字段
# 2、Django默认用户模型类中的一些验证方法我们需要使用
class User(AbstractUser):

    # 添加该字段记录用户手机号
    mobile = models.CharField(
        max_length=11, unique=True, verbose_name='手机号'
    )

    # 新增 email_active 字段
    # 用于记录邮箱是否激活, 默认为 False: 未激活
    email_active = models.BooleanField(default=False,
                                       verbose_name='邮箱验证状态')


    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
