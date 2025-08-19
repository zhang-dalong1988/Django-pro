from django.contrib import admin
from django.urls import path, include  # new

urlpatterns = [
    # Django 管理员
    path("admin/", admin.site.urls),
    # 用户管理
    # path("accounts/", include("django.contrib.auth.urls")),  # 新增
    path("accounts/", include("allauth.urls")),  # 新增
    # 本地应用
    path("", include("pages.urls")),
]
