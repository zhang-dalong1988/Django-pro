# 在线书店项目

## 准备

```bash
# 创建项目目录
$ cd code
$ mkdir ch3-bookstore
$ cd ch3-bookstore
# 创建 Django 项目
$ django-admin startproject django_project .
# 启动开发服务器进行验证
$ python manage.py runserver
# 导出依赖
$ pip freeze > requirements.txt
```

**requirements.txt**

```
asgiref==3.9.1
Django==5.2.4
psycopg-binary==3.2.9
sqlparse==0.5.3
tzdata==2025.2
```

## Docker

分别创建 `Dockerfile`、`docker-compose.yml` 以及 `.dockerignore` 文件

**Dockerfile**

```dockerfile
FROM python:3.13.5-slim-bullseye

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
```

**docker-compose.yml**

```yaml
name: ch3-bookstore

services:
  web:
    build: .
    command: python /code/manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - 8000:8000
    depends_on:
      - db

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - "POSTGRES_HOST_AUTH_METHOD=trust"

volumes:
  postgres_data:
```

**.dockerignore**

```
.venv
.git
.gitignore
```

**验证环境搭建**

```bash
$ docker-compose up -d --build
```

> 刷新 `http://127.0.0.1:8000/` 的 Django 欢迎页面。

## PostgreSQL

更新 `django_project/settings.py` 文件

```python
# django_project/settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",
        "PORT": 5432,
    }
}
```

> 确保刷新网络浏览器中的主页，以确认一切仍然正常工作。

## 自定义用户模型

在项目的生命周期中，一定会需要对内置的 `User` 模型进行更改，如果你没有从你运行的第一个 `migrate` 命令前就使用自定义用户模型，那么你就会面临一系列的痛苦，因为 `User` 在 Django 内部与其他部分紧密交织在一起。在项目中途切换到自定义用户模型是很有挑战性的。

- 在很多老项目中，通常为 User 模型添加一个 [OneToOneField](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#onetoonefield)，通常称为 Profile 模型。
- 如今，使用自定义用户模型是更常见的方法。Django 提供了多种实现选择：
  - 扩展[AbstractUser](https://docs.djangoproject.com/zh-hans/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project)，保留默认的`User` 字段和权限。
  - 扩展[AbstractBaseUser](https://docs.djangoproject.com/zh-hans/5.2/topics/auth/customizing/#specifying-a-custom-user-model)，它更加细致和灵活，但需要更多的工作。

以下，我们将坚持使用更简单的 `AbstractUser`，因为如果需要，以后可以添加 `AbstractBaseUser`。

项目添加自定义用户模型有四个步骤：

1. 创建一个`CustomUser`模型
2. 更新`django_project/settings.py`
3. 自定义`UserCreationForm`和`UserChangeForm`
4. 将自定义用户模型添加到`admin.py`

**创建 CustomUser 模型**

创建 `accounts` 应用，用于管理用户。

```bash
$ docker-compose exec web python manage.py startapp accounts
```

创建一个新的 `CustomUser` 模型，它扩展了 `AbstractUser`。相当于创建一个副本，其中 `CustomUser` 现在继承了 `AbstractUser` 的所有功能，但我们可以根据需要覆盖或添加新功能。我们现在还没有进行任何更改，所以包含 Python `pass`语句，它充当我们未来代码的占位符。

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    pass
```

安装/注册 `accounts` 应用，并且配置 `AUTH_USER_MODEL`，这表示我们的项目使用 `CustomUser` 模型作为用户模型而不是使用默认的 `User` 模型。

```python
# django_project/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 本地应用
    "accounts.apps.AccountsConfig",  # 新增
]
...
AUTH_USER_MODEL = "accounts.CustomUser"  # 新增
```

创建针对 `accounts` 应用的数据库迁移

```bash
$ docker-compose exec web python manage.py makemigrations accounts
```

运行 `migrate` 来第一次初始化数据库

```shell
$ docker-compose exec web python manage.py migrate
```

## 自定义用户表单

用户模型需要在 Django Admin 中进行管理，因此我们需要更新内置表单，指向 `CustomUser` 而不是 `User`。在你的文本编辑器中创建一个新文件 `accounts/forms.py`，并输入以下代码来切换到 `CustomUser`。

```python
# accounts/forms.py
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "username",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "username",
        )
```

通过[get_user_model](https://docs.djangoproject.com/zh-hans/5.2/topics/auth/customizing/#django.contrib.auth.get_user_model)导入了 `CustomUser` 模型，它查找我们在 `settings.py` 中的 `AUTH_USER_MODEL` 配置。

接下来，我们导入[UserCreationForm](https://docs.djangoproject.com/zh-hans/5.2/topics/auth/default/#django.contrib.auth.forms.AdminUserCreationForm)和[UserChangeForm](https://docs.djangoproject.com/zh-hans/5.2/topics/auth/default/#django.contrib.auth.forms.UserChangeForm)，它们都将被扩展。

然后创建两个新表单: `CustomUserCreationForm` 和 `CustomUserChangeForm` 它们扩展了上面导入的基本用户表单，并指定替换我们的`CustomUser`模型并显示`email`和`username`字段。`password` 字段默认隐含包含，因此不需要在这里也显式命名。

## 自定义用户管理

更新我们的 `accounts/admin.py` 文件。管理员是操作用户数据的常见场所，内置的 `User` 与管理员之间存在紧密的耦合。

我们将把现有的 `UserAdmin` 扩展到 `CustomUserAdmin`，并告诉 Django 使用我们的新表单和自定义用户模型。我们也可以列出我们想要的[Django 认证系统组件的 API](https://docs.djangoproject.com/zh-hans/5.2/ref/contrib/auth/#django-contrib-auth)，但目前只关注三个：电子邮件、用户名和超级用户状态。

```python
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "is_superuser",
    ]


admin.site.register(CustomUser, CustomUserAdmin)
```

## 创建超级用户

```shell
# 创建超级用户
# 用户名： test1
# 密码： testpass1
# 邮箱： test1@example.com
$ docker-compose exec web python manage.py createsuperuser
```

> 刷新 `http://127.0.0.1:8000/admin/` 的 Django 管理页面，使用刚刚创建的超级用户登录。

## 测试

无论独立开发者还是在团队，测试都很重要。用 Django 联合创始人 Jacob Kaplan-Moss 的话来说，"没有测试的代码在设计上就是最糟糕的。"

有两种主要类型的测试：

- **单元测试** -- 体量小、执行快速，专注于测试特定功能模块的独立性能
- **集成测试** -- 规模大、运行较慢，用于验证整个应用系统或跨多个界面的用户流程 (如支付流程) 的完整性

在开发过程中，应该优先编写大量的单元测试，同时辅以少量但关键的集成测试。

Python 语言内置了强大的[单元测试框架](https://docs.python.org/3/library/unittest.html)，而 Django 则通过其[自动测试框架](https://docs.djangoproject.com/zh-hans/5.2/topics/testing/)对其进行了扩展，使其更适合 Web 开发环境。编写充分的测试用例绝非浪费时间，相反，它们能在项目后期为你节省大量排错和维护的时间成本。

值得注意的是，我们不需要对所有内容都进行测试。Django 框架本身的功能已经在其源代码中包含了全面的测试覆盖。例如，如果我们使用 Django 默认的`User`模型，就无需再对其进行测试。然而，由于我们创建了自定义的`CustomUser`模型，我们就有责任为其编写相应的测试用例，确保其按预期工作。

在 Django 中编写单元测试时，我们主要使用 [TestCase](https://docs.djangoproject.com/zh-hans/5.2/topics/testing/tools/#provided-test-case-classes) 类，这是 Python 标准库中 [TestCase](https://docs.python.org/3/library/unittest.html#unittest.TestCase) 的增强版本，专为 Django 应用程序测试而设计。当我们使用 `startapp` 命令创建 `accounts` 应用时，Django 已经自动为我们生成了一个 `tests.py` 文件，不过目前它还是空白的。现在是时候为它添加有意义的测试内容了！

在编写测试方法时，有一个重要的约定：所有测试方法必须以 `test` 作为前缀，这样 Django 的测试运行器才能自动识别并执行它们。另外，为测试方法取一个详细且描述性强的名称是非常有价值的实践，尤其是在大型项目中，随着时间推移可能会累积数百甚至数千个测试用例，清晰的命名能让你快速定位和理解每个测试的目的。

```python
# accounts/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase


class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="will", email="will@email.com", password="testpass123"
        )
        self.assertEqual(user.username, "will")
        self.assertEqual(user.email, "will@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="superadmin", email="superadmin@email.com", password="testpass123"
        )
        self.assertEqual(admin_user.username, "superadmin")
        self.assertEqual(admin_user.email, "superadmin@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
```

运行测试

```bash
$ docker-compose exec web python manage.py test
```

## Git

```bash
$ git add .
$ git commit -m "ch3-创建在线书店项目，并且添加自定义用户模型"
$ git push
```
