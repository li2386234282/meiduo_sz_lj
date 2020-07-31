from celery import Celery


celery_app = Celery('meiduo')


# 里面的参数为我们创建的 config 配置文件:
celery_app.config_from_object('celery_tasks.config')

celery_app.autodiscover_tasks(['celery_tasks.sms'])
celery_app.autodiscover_tasks('celery_tasks.sms','celery_tasks.email')