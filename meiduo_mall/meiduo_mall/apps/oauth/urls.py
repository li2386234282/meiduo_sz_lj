from django.urls import re_path

urlpatterns = [
    # 获取 QQ 扫码登录链接
    re_path(r'^qq/authorization/$', views.QQFirstView.as_view()),
]

