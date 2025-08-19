from django.urls import path

from .views import HomePageView, AboutPageView  # 新增

urlpatterns = [
    path("about/", AboutPageView.as_view(), name="about"),  # 新增
    path("", HomePageView.as_view(), name="home"),
]
