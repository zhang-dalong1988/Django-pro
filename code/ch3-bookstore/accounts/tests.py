from django.contrib.auth import get_user_model
from django.test import TestCase


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
        self.assertEqual(admin_user.email, "superadmin@email.com")  # 验证超级用户电子邮件是否正确
        self.assertTrue(admin_user.is_active)  # 验证超级用户是否处于激活状态
        self.assertTrue(admin_user.is_staff)  # 验证超级用户是工作人员
        self.assertTrue(admin_user.is_superuser)  # 验证超级用户是超级用户