from django.db import models

class BaseModel(models.Model):


    #创建时间
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')


    #更新时间
    updata_time = models.DateTimeField(auto_now_add=True,verbose_name='更新时间')


    class Meta:

        #说明是抽象类型，抽象类型不会创建表
        abstract = True