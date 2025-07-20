from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomUserCreationForm


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm # 使用自定义表单
    success_url = reverse_lazy("login")  # 注册成功后重定向到登录页面
    template_name = "registration/signup.html"  # 注册页面模板