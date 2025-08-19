# 3. PostgreSQL

在 Django 中，"玩具应用"和生产就绪应用之间最直接的区别之一就是数据库。Django 默认使用 SQLite 作为本地开发的选择，因为它小巧、快速且基于文件，使用起来很方便。无需额外的安装或配置。

然而，这种便利是有代价的。一般来说，SQLite 不是专业网站的好选择。虽然在本地原型设计时使用 SQLite 是可以的，但在生产项目中实际使用 SQLite 的情况很少见。

Django 内置支持五种数据库：PostgreSQL、MariaDB、MySQL、Oracle 和 SQLite。在本书中我们将使用 PostgreSQL，因为它是 Django 开发者最受欢迎的选择。然而，Django ORM（对象关系映射器）的美妙之处在于，即使我们想使用 MySQL、MariaDB 或 Oracle，我们编写的实际 Django 代码几乎是相同的。Django ORM 会自动为我们处理从 Python 代码到为每个数据库配置的 SQL 的转换，如果你仔细想想，这是相当令人惊叹的。

使用非基于文件的数据库的挑战在于，如果你想在自己的计算机上忠实地模拟生产环境，就必须在本地安装和运行它们。而我们确实希望这样做！虽然 Django 为我们处理了数据库之间切换的细节，但如果你在本地开发中使用 SQLite 而在生产中使用不同的数据库，不可避免地会出现一些小的、难以捕获的错误。因此，最佳实践是在本地和生产中使用相同的数据库。

在本章中，我们将从一个使用 SQLite 数据库的新 Django 项目开始，然后切换到 Docker 和 PostgreSQL。

## 3.1 Django 设置

在命令行中，确保你已经导航回到桌面上的 code 文件夹。你可以通过两种方式做到这一点。要么输入`cd ..`向"上"移动一级，这样如果你当前在 Desktop/code/hello 中，你将移动到 Desktop/code。或者你可以简单地在 Windows 上输入`cd onedrive\desktop`，在 macOS 上输入`cd ~/desktop/code`，这将直接带你到 code 目录。然后为本章的代码创建一个名为 ch3-postgresql 的新目录。

```bash
# Windows
$ cd onedrive\desktop
$ mkdir ch3-postgresql

# macOS
$ cd ~/desktop/code
$ mkdir ch3-postgresql
```

我们将遵循创建新 Django 项目的标准步骤：创建专用虚拟环境、激活它并安装 Django。

```bash
# Windows
$ python -m venv .venv
$ Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
$ .venv\Scripts\Activate.ps1
(.venv) $ python -m pip install django~=4.0.0

# macOS
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ python3 -m pip install django~=4.0.0
```

接下来我们可以创建一个名为 django_project 的新项目，迁移我们的数据库以初始化它，并使用 runserver 启动本地服务器。

```bash
(.venv) $ django-admin startproject django_project .
(.venv) $ python manage.py migrate
(.venv) $ python manage.py runserver
```

通常我不建议在配置自定义用户模型之前对新项目运行 migrate。否则 Django 会将数据库绑定到内置的 User 模型，这在项目后期很难修改。我们将在第 3 章中正确介绍这一点，但由于本章主要用于演示目的，在这里使用默认 User 模型是一次性的例外。

通过在网络浏览器中导航到 http://127.0.0.1:8000/ 来确认一切正常工作。你可能需要刷新页面，但应该看到熟悉的 Django 欢迎页面。

在切换到 Docker 之前的最后一步是使用我们在上一章中学到的命令创建 requirements.txt 文件。

```bash
(.venv) $ pip freeze > requirements.txt
```

这将生成一个新的 requirements.txt 文件，包含我们当前虚拟环境的固定内容。

## 3.2 Docker 配置

要切换到 Docker，首先停用我们的虚拟环境，然后在文本编辑器中创建新的 Dockerfile 和 docker-compose.yml 文件，它们将分别控制我们的 Docker 镜像和容器。

```bash
(.venv) $ deactivate
$
```

Dockerfile 与第 1 章中的相同。

**Dockerfile：**

```dockerfile
# 拉取基础镜像
FROM python:3.10.4-slim-bullseye

# 设置环境变量
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /code

# 安装依赖项
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# 复制项目
COPY . .
```

在构建镜像之前，确保创建.dockerignore 文件。

**.dockerignore：**

```
.venv
.git
.gitignore
```

注意，如果你使用`docker build .`命令构建初始镜像，它比上一章快得多。

```bash
$ docker build .
...
---> Using cache
```

这是因为每当你构建新的 Dockerfile 时，Docker 会自动检查是否可以使用以前构建的缓存结果。由于这个 Dockerfile 与第 1 章中的相同，除了将本地文件与容器文件系统上的文件同步的最终 COPY 命令外，其他一切都相同。

这种缓存意味着 Dockerfile 的顺序对性能原因很重要。为了避免不断使缓存失效，我们从不太可能更改的命令开始 Dockerfile，而将更可能更改的命令（如复制本地文件系统）放在最后。

现在是 docker-compose.yml 文件的时候了，它也与我们在第 1 章中看到的相匹配。

**docker-compose.yml：**

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
```

### 3.2.1 分离模式

我们现在将启动我们的容器，但这次使用分离模式，这需要-d 或--detach 标志（它们做同样的事情）。

```bash
$ docker-compose up -d
```

分离模式在后台运行容器，这意味着我们可以使用单个命令行选项卡，而不需要同时打开另一个。这节省了我们在两个命令行选项卡之间不断切换的时间。缺点是如果/当出现错误时，输出并不总是可见的。所以如果你的屏幕在某个时候与本书不匹配，尝试输入`docker-compose logs`来查看当前输出并调试任何问题。

你可能会在命令底部看到"Warning: Image for service web was built because it did not already exist"消息。Docker 在容器内自动为我们创建了一个新镜像。正如我们将在本书后面看到的，当软件包更新时，添加--build 标志来强制镜像构建是必要的，因为默认情况下，Docker 会寻找软件的本地缓存副本并使用它，这提高了性能。

要确认一切正常工作，请返回网络浏览器中的 http://127.0.0.1:8000/。刷新页面再次看到Django欢迎页面。

由于我们现在在 Docker 内工作而不是在本地，我们必须在传统命令前加上`docker-compose exec [service]`，其中我们指定服务的名称。例如，要创建超级用户帐户，而不是输入`python manage.py createsuperuser`，更新的命令现在看起来像下面的行，使用 web 服务。

```bash
$ docker-compose exec web python manage.py createsuperuser
```

**注意：** 如果你使用的是较新的基于 M1 的 macOS 计算机，这个命令可能会产生以下神秘错误：`django.db.utils.OperationalError: SCRAM authentication requires libpq version 10 or above`。目前在 ARM 上的 libpg 中有一个上游错误，它正在构建错误的库版本。修复方法是通过在安装 Python 的初始 FROM 命令中添加`--platform=linux/amd64`来更新 Dockerfile 的第一行以指定正确的本地平台。

**Dockerfile：**

```dockerfile
# 拉取基础镜像
FROM --platform=linux/amd64 python:3.10.4-slim-bullseye
...
```

对于用户名选择 sqliteadmin ，电子邮件地址选择 sqliteadmin@email.com，并选择你选择的密码。我经常使用 testpass123。

然后直接导航到 http://127.0.0.1:8000/admin 的管理员并登录。你将被重定向到管理员主页。注意右上角 sqliteadmin 是用户名。

Django 对多种语言有令人印象深刻的支持，所以如果你想看到管理员、表单和其他默认消息使用英语以外的语言，尝试调整 django_project/settings.py 中的 LANGUAGE_CODE 配置，它自动设置为美式英语，en-us。

继续，如果你点击 Users 按钮，它会带我们到 Users 页面，我们可以确认只创建了一个用户。

重要的是要在这一点上强调 Docker 的另一个方面：到目前为止，我们一直在 Docker 内更新我们的数据库——目前由 db.sqlite3 文件表示。这意味着实际的 db.sqlite3 文件每次都在变化。由于我们的 docker-compose.yml 配置中的卷挂载，每个文件更改也已复制到我们本地计算机上的 db.sqlite3 文件中。你可以退出 Docker，启动 shell，使用`python manage.py runserver`启动服务器，并在此时看到完全相同的管理员登录，因为底层 SQLite 数据库是相同的。

## 3.3 PostgreSQL 配置

PostgreSQL 是一个几乎可以被任何编程语言使用的数据库。但如果你仔细想想，编程语言——它们都以某种方式变化——如何连接到数据库本身？

答案是通过数据库适配器！这就是 Psycopg，Python 最受欢迎的数据库适配器。如果你想了解更多关于 Psycopg 如何工作的信息，这里有一个链接到官方网站上更完整的描述。

Psycopg 3.0 最近发布，但许多包和托管提供商仍然专注于 Psycopg2，所以这就是我们将使用的。请注意，实际上有两个版本的 Pyscopg2 可用：pyscopg2 和 pyscopg2-binary。我们将在本书中使用二进制版本，因为它更简单易用，对大多数网站来说都很好用。使用非二进制版本需要多个额外的配置步骤，只与真正大规模的网站相关。如果在很久以后你发现数据库速度慢，调查 pyscopg2 与 psycopg2-binary 是值得花时间的。但开始时不是。

要安装它，首先用`docker-compose down`停止运行 Docker 容器。

```bash
$ docker-compose down
```

现在暂停并思考将包安装到 Docker 中与本地虚拟环境意味着什么是很重要的。在传统项目中，我们会从命令行运行命令`python -m pip install psycopg2-binary==2.9.3`来安装 Pyscopg2。但我们现在正在使用 Docker。

有两个选择。第一个是在本地安装 psycopg2-binary，然后 pip freeze 我们的虚拟环境来更新 requirements.txt。如果我们要使用本地环境，这可能有意义。但由于我们致力于 Docker，我们可以跳过该步骤，而只是用 psycopg2-binary 包更新 requirements.txt。我们不需要进一步更新实际的虚拟环境，因为我们不太可能使用它。如果我们曾经这样做，我们可以基于 requirements.txt 更新它。

在文本编辑器中打开现有的 requirements.txt 文件，并在底部添加 psycopg2-binary==2.9.3。

**requirements.txt：**

```
asgiref==3.5.2
Django==4.0.4
sqlparse==0.4.2
psycopg2-binary==2.9.3
```

在我们的 PostgreSQL 配置更改结束时，我们将构建新镜像并启动我们的容器。但还没有。

### 3.3.1 docker-compose.yml 更新

在现有的 docker-compose.yml 文件中添加一个名为 db 的新服务。这意味着在我们的 Docker 主机内将运行两个单独的容器：web 用于 Django 本地服务器，db 用于我们的 PostgreSQL 数据库。

web 服务依赖于 db 服务运行，所以我们将向 web 添加一行称为 depends_on 来表示这一点。

在 db 服务中，我们指定要使用的 PostgreSQL 版本。截至撰写本文时，Heroku 支持版本 13 作为最新版本，所以这就是我们将使用的。Docker 容器是短暂的，意味着当容器停止运行时，所有信息都会丢失。这显然对我们的数据库来说是个问题！解决方案是创建一个名为 postgres_data 的卷挂载，然后将其绑定到容器内位置/var/lib/postgresql/data/的专用目录。最后一步是为 db 的环境添加信任身份验证。对于有许多数据库用户的大型数据库，建议对权限更明确，但当只有一个开发者时，此设置是一个好选择。

以下是更新后的文件：

**docker-compose.yml：**

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

### 3.3.2 数据库配置

第三步也是最后一步是更新 django_project/settings.py 文件以使用 PostgreSQL 而不是 SQLite。在文本编辑器中向下滚动到 DATABASES 配置。

默认情况下，Django 指定 sqlite3 作为数据库引擎，给它命名为 db.sqlite3，并将其放在 BASE_DIR，这意味着在我们的项目级目录中。

```python
# django_project/settings.py

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

要切换到 PostgreSQL，我们将更新 ENGINE 配置。PostgreSQL 需要 NAME、USER、PASSWORD、HOST 和 PORT。为了方便，我们将前三个设置为 postgres，HOST 设置为 db，这是我们在 docker-compose.yml 中设置的服务名称，PORT 设置为 5432，这是默认的 PostgreSQL 端口。

**代码示例：**

```python
# django_project/settings.py

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",  # 在docker-compose.yml中设置
        "PORT": 5432,  # 默认postgres端口
    }
}
```

就是这样！我们可以构建包含 psycopg2-binary 的新镜像，并使用以下单个命令在分离模式下启动两个容器：

```bash
$ docker-compose up -d --build
```

如果你刷新 http://127.0.0.1:8000/ 的 Django 欢迎页面，它应该工作，这意味着 Django 已经通过 Docker 成功连接到 PostgreSQL。

## 3.4 新数据库迁移

由于我们现在使用 PostgreSQL 而不是 SQLite，我们的数据库是空的。如果你通过输入`docker-compose logs`再次查看当前日志，你会看到像"You have 18 unapplied migrations(s)"这样的抱怨。

为了强化这一点，访问 http://127.0.0.1:8000/admin/ 的管理员并登录。我们之前的超级用户帐户 sqliteadmin 和 testpass123 会工作吗？

不会！我们看到 ProgrammingError at /admin。要解决这种情况，我们可以在 Docker 内迁移和创建一个将访问 PostgreSQL 数据库的超级用户。

```bash
$ docker-compose exec web python manage.py migrate
$ docker-compose exec web python manage.py createsuperuser
```

我们应该叫我们的超级用户什么？让我们使用 postgresqladmin ，为了测试目的，将电子邮件设置为 postgresqladmin@email.com ，密码设置为 testpass123。

在网络浏览器中导航到 http://127.0.0.1:8000/admin/ 的管理页面并输入新的超级用户登录信息。

在右上角显示我们现在以 postgresadmin 登录，而不是 sqliteadmin。此外，你可以点击主页上的 Users 选项卡并访问 Users 部分，看到我们唯一的用户是新的超级用户帐户。

记住用`docker-compose down`停止我们正在运行的容器。

```bash
$ docker-compose down
```

## 3.5 Git 版本控制

让我们用 Git 保存我们的更改。初始化一个新的 Git 存储库并检查当前状态。

```bash
$ git init
$ git status
```

在创建第一次提交之前，向项目根目录添加.gitignore 文件总是一个好主意。我们的现在将有四行。

**.gitignore：**

```
.venv
__pycache__/
db.sqlite3
.DS_Store  # 仅Mac
```

再次使用`git status`检查两者都不再被 Git 跟踪，然后添加所有其他更改并包含提交消息。

```bash
$ git status
$ git add .
$ git commit -m 'ch3'
```

第 3 章的官方源代码可在 Github 上获得。

## 3.6 结论

本章的目标是演示 Docker 和 PostgreSQL 如何在 Django 项目上协同工作。对许多开发者来说，在 SQLite 数据库和 PostgreSQL 之间切换最初是一个心理飞跃。

关键点是，使用 Docker 我们不再需要在本地虚拟环境中。Docker 是我们的虚拟环境...以及我们的数据库，如果需要的话还有更多。Docker 主机本质上取代了我们的本地操作系统，在其中我们可以运行多个容器，例如用于我们的 Web 应用程序和数据库，它们都可以被隔离并单独运行。

在下一章中，我们将开始我们的在线书店项目。让我们开始吧！
