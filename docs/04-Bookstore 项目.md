# 第 4 章：书店项目

现在是时候构建本书的主要项目——一个在线书店了。在本章中，我们将开始一个新项目，切换到 Docker，添加自定义用户模型，并编写我们的第一个测试。

让我们从创建一个新的 Django 项目开始。从桌面创建一个名为 ch4-bookstore 的新目录，然后创建并激活一个新的 Python 虚拟环境。接下来我们将安装 Django 和连接 PostgreSQL 数据库所需的 psycopg2-binary 适配器。

## 1. 项目初始化

### 1.1 Windows 环境设置

```shell
$ cd onedrive\desktop
$ mkdir ch4-bookstore
$ cd ch4-bookstore
$ python -m venv .venv
$ Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
$ .venv\Scripts\Activate.ps1
(.venv) $ python -m pip install django~=4.0.0 psycopg2-binary==2.9.3
```

### 1.2 macOS 环境设置

```shell
$ cd ~/desktop/code
$ mkdir ch4-bookstore
$ cd ch4-bookstore
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ python3 -m pip install django~=4.0.0 psycopg2-binary==2.9.3
```

### 1.3 创建 Django 项目

我们使用 `startproject` 命令创建名为 `django_project` 的新 Django 项目。确保不要忘记命令末尾的句点 `.`，否则 Django 会创建一个我们不需要的额外目录。然后使用 `runserver` 启动本地 Django Web 服务器并确认一切正常工作。

```shell
(.venv) $ django-admin startproject django_project .
(.venv) $ python manage.py runserver
```

在您的 Web 浏览器中访问 http://127.0.0.1:8000/，您应该会看到友好的 Django 欢迎页面。

在命令行中，您可能会看到关于"18 个未应用的迁移"的警告。现在可以安全地忽略这个警告，因为我们即将切换到 Docker 和 PostgreSQL。

最后，使用 Control+c 停止本地服务器，并在文本编辑器中创建一个 requirements.txt 文件，包含我们 Python 虚拟环境的当前内容。

```shell
(.venv) $ pip freeze > requirements.txt
```

新文件应该包含与 Django 一起安装的三个包——Django、asgiref、sqlparse——以及 psycopg2-binary。

**requirements.txt**

```
asgiref==3.5.2
Django==4.0.4
psycopg2-binary==2.9.3
sqlparse==0.4.2
```

## 2. Docker 配置

现在我们可以在项目中切换到 Docker。继续停止本地服务器（Control+c）并退出虚拟环境 shell。

```shell
(.venv) $ deactivate
$
```

Docker 应该已经从上一章安装并运行桌面应用程序。我们需要一个 Dockerfile 用于我们的镜像和一个 docker-compose.yml 文件来运行容器。这个过程与我们在第 3 章中所做的完全相同。

在文本编辑器中，在现有 manage.py 文件旁边的基础目录中创建新的 Dockerfile 和 docker-compose.yml 文件。然后将以下代码添加到每个文件中。

### 2.1 Dockerfile 配置

```dockerfile
# 拉取基础镜像
FROM python:3.10.4-slim-bullseye

# 设置环境变量
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /code

# 安装依赖
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# 复制项目
COPY . .
```

### 2.2 docker-compose.yml 配置

```yaml
version: "3.9"

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
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - "POSTGRES_HOST_AUTH_METHOD=trust"

volumes:
  postgres_data:
```

请记住，如果您使用的是较新的基于 M1 的 macOS 计算机，可能需要通过在安装 Python 的初始 FROM 命令中添加 `--platform=linux/amd64` 来指定正确的本地平台。

```dockerfile
# 拉取基础镜像
FROM --platform=linux/amd64 python:3.10.4-slim-bullseye
...
```

### 2.3 忽略文件配置

在构建镜像之前，确保也创建 .dockerignore 文件和 .gitignore 文件。

**.dockerignore**

```
.venv
.git
.gitignore
```

**.gitignore**

```
.venv
**__pycache__**/
db.sqlite3
.DS_Store # 仅限 Mac
```

### 2.4 构建和运行容器

现在我们可以用一个命令构建镜像并运行容器。

```shell
$ docker-compose up -d --build
```

现在在 Web 浏览器中访问 http://127.0.0.1:8000/ 并点击刷新。应该是相同的友好 Django 欢迎页面，尽管现在在 Docker 内部运行。

## 3. PostgreSQL 配置

最后一步是切换到 PostgreSQL。尽管我们已经安装了 psycopg2-binary 并在 docker-compose.yml 文件中提供了 PostgreSQL，但我们仍然必须明确告诉 Django 使用什么数据库，我们可以在 django_project/settings.py 文件中做到这一点。请记住，默认情况下 Django 将使用 SQLite 数据库。

更新的代码与上一章相同。

**django_project/settings.py**

```python
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

确保刷新 Web 浏览器的主页以确认一切仍然正常工作。

## 4. 自定义用户模型

现在我们来到新材料！我们首先实现一个自定义用户模型，Django 官方文档"强烈推荐"这样做。为什么？因为在项目生命周期的某个时候，您需要对内置的 User 模型进行更改，如果您没有从运行的第一个 migrate 命令开始就使用自定义用户模型，那么您将面临巨大的困难，因为 User 与 Django 内部的其余部分紧密交织在一起。在项目中期切换到自定义用户模型是具有挑战性的。

许多人困惑的一点是，自定义用户模型只在 Django 1.5 中添加。在那之前，推荐的方法是向 User 添加一个 OneToOneField，通常称为 Profile 模型。您经常会在较旧的项目中看到这种设置。

但现在使用自定义用户模型是更常见的方法。然而，与许多 Django 相关的事情一样，有实现选择：要么扩展 AbstractUser（保留默认的 User 字段和权限），要么扩展 AbstractBaseUser（更加细粒度和灵活，但需要更多工作）。

在本书中我们将坚持使用更简单的 AbstractUser，因为如果需要的话，AbstractBaseUser 可以稍后添加。

### 4.1 自定义用户模型实现步骤

向我们的项目添加自定义用户模型有四个步骤：

1. 创建 CustomUser 模型
2. 更新 django_project/settings.py
3. 自定义 UserCreationForm 和 UserChangeForm
4. 将自定义用户模型添加到 admin.py

### 4.2 创建 CustomUser 模型

第一步是创建一个 CustomUser 模型，它将存在于自己的应用程序中。我喜欢将这个应用程序命名为 accounts。从现在开始，我们将在 Docker 本身内运行大部分命令。因为我们在 docker-compose.yml 的 web 服务中配置了卷，Docker 内的任何文件系统更改都将反映在本地文件系统中。

```shell
$ docker-compose exec web python manage.py startapp accounts
```

创建一个扩展 AbstractUser 的新 CustomUser 模型。这意味着我们本质上是在制作一个副本，其中 CustomUser 现在继承了 AbstractUser 的所有功能，但我们可以根据需要覆盖或添加新功能。我们还没有进行任何更改，所以包含 Python pass 语句，它作为我们未来代码的占位符。

**accounts/models.py**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    pass
```

### 4.3 更新 settings.py

现在进入并更新我们的 settings.py 文件中的 INSTALLED_APPS 部分，告诉 Django 我们的新 accounts 应用程序。我们还想在文件底部添加一个 AUTH_USER_MODEL 配置，这将导致我们的项目使用 CustomUser 而不是默认的 User 模型。

**django_project/settings.py**

```python
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

### 4.4 创建数据库迁移

是时候为更改创建迁移文件了。我们将在命令中添加可选的应用程序名称 accounts，以便只包含对该应用程序的更改。

```shell
$ docker-compose exec web python manage.py makemigrations accounts
```

输出：

```
Migrations for 'accounts':
  accounts/migrations/0001_initial.py
    - Create model CustomUser
```

然后运行 migrate 来首次初始化数据库。

```shell
$ docker-compose exec web python manage.py migrate
```

输出：

```
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, sessions
Running migrations:
  No migrations to apply.
```

## 5. 自定义用户表单

用户模型可以在 Django 管理员中创建和编辑。因此，我们还需要更新内置表单以指向 CustomUser 而不是 User。在文本编辑器中创建一个名为 accounts/forms.py 的新文件，并输入以下代码以切换到 CustomUser。

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

在最顶部，我们通过 get_user_model 导入了 CustomUser 模型，它查看我们在 settings.py 中的 AUTH_USER_MODEL 配置。这可能感觉比直接在这里导入 CustomUser 更加循环，但它强化了对自定义用户模型进行单一引用的想法，而不是在整个项目中直接引用它。

接下来我们导入 UserCreationForm 和 UserChangeForm，它们都将被扩展。

然后创建两个新表单——CustomUserCreationForm 和 CustomUserChangeForm——它们扩展上面导入的基本用户表单，并指定交换到我们的 CustomUser 模型并显示字段 email 和 username。密码字段默认隐式包含，因此也不需要在这里明确命名。

## 6. 自定义用户管理

最后，我们必须更新我们的 accounts/admin.py 文件。管理员是操作用户数据的常见场所，内置 User 和管理员之间存在紧密耦合。

我们将现有的 UserAdmin 扩展为 CustomUserAdmin，并告诉 Django 使用我们的新表单和自定义用户模型。我们还可以列出我们想要的任何用户属性，但现在只关注三个：email、username 和超级用户状态。

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

呼！前期有点代码，但这可以节省以后的很多麻烦。

## 7. 创建超级用户

确认我们的自定义用户模型正常运行的好方法是创建一个超级用户帐户，这样我们就可以登录管理员。此命令将在底层访问 CustomUserCreationForm。

```shell
$ docker-compose exec web python manage.py createsuperuser
```

我使用了用户名 wsv、电子邮件 will@wsvincent.com 和密码 testpass123。您可以在这里使用自己的首选变体。

在您的 Web 浏览器中打开页面 http://127.0.0.1:8000/admin 并登录。您应该在登录后页面的右上角看到您的超级用户名。

您还可以点击 Users 部分查看超级用户帐户的电子邮件和用户名。

## 8. 测试

由于我们已经向项目添加了新功能，我们应该对其进行测试。无论您是独立开发人员还是在团队中工作，测试都很重要。用 Django 联合创始人 Jacob Kaplan-Moss 的话来说，"没有测试的代码在设计上就是坏的。"

有两种主要类型的测试：

- **单元测试**：小型、快速且隔离到特定功能片段
- **集成测试**：大型、缓慢且用于测试整个应用程序或涵盖多个屏幕的用户流程（如支付）

您应该编写许多单元测试和少量集成测试。

Python 编程语言包含自己的单元测试框架，Django 的自动化测试框架通过多个添加将其扩展到 Web 上下文中。没有理由不编写大量测试；它们会为您节省时间。

重要的是要注意，并非所有内容都需要测试。例如，任何内置的 Django 功能在源代码中已经包含测试。如果我们在项目中使用默认的 User 模型，我们就不需要测试它。但是由于我们创建了一个 CustomUser 模型，我们应该测试它。

### 8.1 单元测试

要在 Django 中编写单元测试，我们使用 TestCase，它本身是 Python TestCase 的扩展。我们的 accounts 应用程序已经包含一个 tests.py 文件，当使用 startapp 命令时会自动添加该文件。目前它是空白的。让我们修复它！

每个方法都必须以 test 为前缀，以便由 Django 测试套件运行。对单元测试名称过度描述也是一个好主意，因为成熟的项目有数百甚至数千个测试！

**accounts/tests.py**

```python
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

我们在创建 CustomUserTests 类之前导入了 get_user_model 和 TestCase。在其中有两个单独的测试。test_create_user 确认可以创建新用户。首先，我们将用户模型设置为变量 User，然后通过管理器方法 create_user 创建一个，该方法执行使用适当权限创建新用户的实际工作。

对于 test_create_superuser，我们遵循类似的模式，但引用 create_superuser 而不是 create_user。两个用户之间的区别是超级用户应该将 is_staff 和 is_superuser 都设置为 True。

### 8.2 运行测试

要在 Docker 中运行我们的测试，我们将在传统命令 python manage.py test 前面加上 docker-compose exec web。

```shell
$ docker-compose exec web python manage.py test
```

输出：

```
Found 2 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..

----------------------------------------------------------------------

Ran 2 tests in 0.115s

OK
Destroying test database for alias 'default'...
```

所有测试都通过了，所以我们可以继续。

## 9. Git 版本控制

我们在本章中完成了很多工作，所以这是暂停并通过初始化新的 Git 存储库、添加更改和包含提交消息来提交我们的工作的好时机。

```shell
$ git init
$ git status
$ git add .
$ git commit -m 'ch4'
```

您可以在 Github 上与本章的官方源代码进行比较。

## 10. 总结

我们的书店项目现在正在使用 Docker 和 PostgreSQL 运行，我们已经配置了自定义用户模型。接下来将是用于静态页面的 pages 应用程序。

通过本章的学习，我们完成了以下重要任务：

1. **项目初始化**：创建了新的 Django 项目并设置了虚拟环境
2. **Docker 集成**：配置了 Dockerfile 和 docker-compose.yml 实现容器化部署
3. **PostgreSQL 配置**：切换到生产级数据库系统
4. **自定义用户模型**：实现了可扩展的用户认证系统
5. **管理界面定制**：配置了 Django Admin 以支持自定义用户模型
6. **测试编写**：为自定义功能编写了单元测试
7. **版本控制**：使用 Git 管理项目代码

这些基础设施的建立为后续的功能开发奠定了坚实的基础。
