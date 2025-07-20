from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, resolve  # 新增

from .forms import CustomUserCreationForm  # 新增
from .views import SignupPageView  # 新增


class CustomUserTests(TestCase):
    """
    自定义用户模型测试类
    用于测试CustomUser模型的基本功能是否正常工作
    """

    def test_create_user(self):
        """
        测试创建普通用户功能
        验证:
        1. 用户名是否正确设置
        2. 电子邮件是否正确设置
        3. 用户是否默认处于激活状态
        4. 用户是否默认不是工作人员
        5. 用户是否默认不是超级用户
        """
        User = get_user_model()  # 获取当前项目配置的用户模型类
        user = User.objects.create_user(
            username="will", email="will@email.com", password="testpass123"
        )
        self.assertEqual(user.username, "will")  # 验证用户名是否正确
        self.assertEqual(user.email, "will@email.com")  # 验证电子邮件是否正确
        self.assertTrue(user.is_active)  # 验证用户是否处于激活状态
        self.assertFalse(user.is_staff)  # 验证用户不是工作人员
        self.assertFalse(user.is_superuser)  # 验证用户不是超级用户

    def test_create_superuser(self):
        """
        测试创建超级用户功能
        验证:
        1. 超级用户名是否正确设置
        2. 超级用户电子邮件是否正确设置
        3. 超级用户是否默认处于激活状态
        4. 超级用户是否默认是工作人员
        5. 超级用户是否默认是超级用户
        """
        User = get_user_model()  # 获取当前项目配置的用户模型类
        admin_user = User.objects.create_superuser(
            username="superadmin", email="superadmin@email.com", password="testpass123"
        )
        self.assertEqual(admin_user.username, "superadmin")  # 验证超级用户名是否正确
        self.assertEqual(
            admin_user.email, "superadmin@email.com"
        )  # 验证超级用户电子邮件是否正确
        self.assertTrue(admin_user.is_active)  # 验证超级用户是否处于激活状态
        self.assertTrue(admin_user.is_staff)  # 验证超级用户是工作人员
        self.assertTrue(admin_user.is_superuser)  # 验证超级用户是超级用户


class SignUpPageTests(TestCase):  # 注册页面测试类
    """
    注册页面测试类
    用于测试注册页面的渲染和内容是否符合预期
    """

    def setUp(self):
        """
        测试前置设置
        - 获取注册页面的 URL
        - 发送 GET 请求并保存响应
        """
        url = reverse("signup")  # 通过名称解析注册页面的 URL
        self.response = self.client.get(url)  # 发送 GET 请求并存储响应

    def test_signup_template(self):
        """
        测试注册页面模板
        验证:
        1. 响应状态码是否为200（成功）
        2. 是否使用了正确的模板
        3. 页面是否包含预期的文本内容
        4. 页面是否不包含不应出现的内容
        """
        self.assertEqual(self.response.status_code, 200)  # 验证响应状态码为200（成功）
        self.assertTemplateUsed(
            self.response, "registration/signup.html"
        )  # 验证使用了正确的模板
        self.assertContains(self.response, "注册")  # 验证页面包含"注册"文本
        self.assertNotContains(
            self.response, "嗨！我不应该出现在页面上。"
        )  # 验证页面不包含不应出现的内容

    def test_signup_form(self):
        """
        测试注册表单
        验证:
        1. 响应上下文中的表单是否为自定义用户创建表单
        2. 页面是否包含CSRF令牌（确保表单安全）
        """
        form = self.response.context.get("form")  # 从响应上下文中获取表单对象
        self.assertIsInstance(
            form, CustomUserCreationForm
        )  # 验证表单是否为自定义用户创建表单类的实例
        self.assertContains(
            self.response, "csrfmiddlewaretoken"
        )  # 验证页面是否包含CSRF令牌

    def test_signup_view(self):
        """
        测试注册视图
        验证:
        1. URL路径是否正确解析到SignupPageView视图
        2. 解析的视图函数名称是否与SignupPageView的视图函数名称匹配
        """
        view = resolve("/accounts/signup/")  # 解析注册页面的URL路径
        self.assertEqual(
            view.func.__name__, SignupPageView.as_view().__name__
        )  # 验证解析的视图函数名称与SignupPageView的视图函数名称匹配
