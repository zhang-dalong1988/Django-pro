# 2. 初识 Docker

正确配置本地开发环境仍然是一个巨大的挑战，尽管现代编程在其他方面都有了很大的进步。变量太多了：不同的计算机、操作系统、Django 版本、虚拟环境选项等等。当你在团队环境中工作，每个人都需要相同的设置时，问题只会更加严重。

近年来出现了一个解决方案：Docker。它已经迅速成为许多从事生产级项目的开发人员的默认选择。

有了 Docker，终于可以在本地忠实可靠地重现生产环境，从正确的 Python 版本到安装 Django 和运行生产级数据库等附加服务。这意味着你使用 Mac、Windows 还是 Linux 计算机都不再重要。一切都在 Docker 内部运行。

Docker 还使团队协作变得更加容易。不再需要共享冗长、过时的 README 文件来为团队项目添加新开发人员。相反，使用 Docker 你只需共享两个文件——Dockerfile 和 docker-compose.yml 文件——开发人员就可以确信他们的本地开发环境与团队其他成员完全相同。

Docker 并不是完美的技术。它仍然相对较新，底层复杂，并且正在积极开发中。但它所追求的承诺——一个一致且可共享的开发环境，可以在任何计算机上本地运行或部署到任何服务器——使其成为一个可靠的选择。此时它在公司中也被广泛使用，所以写一本面向"专业人士"的书而不涵盖 Docker 感觉是短视的。

在本章中，我们将更多地了解 Docker 本身，并"Docker 化"我们的第一个 Django 项目。

## 2.1 什么是 Docker？

Docker 是一种通过 Linux 容器隔离整个操作系统的方法，Linux 容器是虚拟化的一种类型。虚拟化起源于计算机科学的早期，当时大型、昂贵的大型机是常态。多个程序员如何使用同一台机器？答案是虚拟化，特别是虚拟机，它们是从操作系统向上的计算机系统的完整副本。

如果你在像 Amazon Web Services（AWS）这样的云提供商那里租用空间，他们通常不会为你提供专用的硬件。相反，你与其他客户共享一台物理服务器。但是因为每个客户都有自己的虚拟机在服务器上运行，对客户来说就好像他们有自己的服务器一样。

这项技术使得从云提供商快速添加或删除服务器成为可能。这在很大程度上是幕后的软件，而不是实际的硬件变更。

虚拟机的缺点是什么？大小和速度。一个典型的客户操作系统很容易占用 700MB 的大小。所以如果一台物理服务器支持三个虚拟机，那就至少占用 2.1GB 的磁盘空间，以及对 CPU 和内存资源的单独需求。

这时 Docker 出现了。关键思想是大多数计算机依赖相同的 Linux 操作系统，那么如果我们从 Linux 层向上虚拟化会怎样？这不是会提供一种轻量级、更快的方式来复制大部分相同的功能吗？答案是肯定的。近年来 Linux 容器已经变得非常流行。对于大多数应用程序——特别是 Web 应用程序——虚拟机提供的资源远超所需，而容器已经绰绰有余。从根本上说，这就是 Docker：一种实现 Linux 容器的方法！

我们可以使用房屋和公寓的类比。虚拟机就像房屋：独立的建筑，有自己的基础设施，包括管道和供暖，以及厨房、浴室、卧室等。Docker 容器就像公寓：它们共享管道和供暖等公共基础设施，但有各种大小来匹配所有者的确切需求。

## 2.2 虚拟环境 vs 容器

虚拟环境是隔离 Python 包的一种方式。借助虚拟环境，一台计算机可以在本地运行多个项目。例如，项目 A 可能使用 Python 3.10 和 Django 4.0 以及其他依赖项；而项目 B 使用 Python 3.5 和 Django 1.11。通过为每个项目创建新的虚拟环境并将 Python 包安装到其中，而不是全局安装在计算机本身上，所有必要的 Python 包都可以根据需要进行维护、管理和更新。

有几种实现虚拟环境的方法，但可以说最简单的是使用已作为 Python 3 标准库一部分安装的 venv 模块。我们很快就会使用 venv 在计算机上本地安装 Django。

虚拟环境和 Docker 容器之间的重要区别是虚拟环境只能隔离 Python 包。它们无法隔离非 Python 软件，如 PostgreSQL 或 MySQL 数据库。虚拟环境仍然依赖于 Python 的全局系统级安装（换句话说，在你的计算机上）。虚拟环境指向现有的 Python 安装；它本身不包含 Python。

Linux 容器更进一步，隔离整个操作系统，而不仅仅是 Python 部分。换句话说，我们将在 Docker 中安装 Python 本身，以及安装和运行生产级数据库。

Docker 本身是一个复杂的主题，我们不会在本书中深入探讨，但是了解其背景和关键组件很重要。如果你想了解更多，我推荐 Dive into Docker 视频课程。

## 2.3 安装 Docker

好了，理论够了。让我们开始一起使用 Docker 和 Django。第一步是在 Docker Hub 上注册一个免费账户，然后在本地机器上安装 Docker 桌面应用程序：

- Docker for Mac
- Docker for Windows

这个下载可能需要一些时间，因为它是一个非常大的文件！此时可以随意伸展一下腿。

一旦 Docker 安装完成，我们可以通过在命令行 shell 中输入命令`docker --version`来确认正确的版本正在运行。它应该至少是版本 18。

```shell
$ docker --version
Docker version 20.10.14, build a224086
```

## 2.4 Docker Hello, World

Docker 自带了一个有用的"Hello, World"镜像，这是运行的第一步。在命令行中输入`docker run hello-world`。这将下载一个官方的 Docker 镜像，然后在容器中运行它。我们稍后会讨论镜像和容器。

```shell
$ docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
7050e35b49f5: Pull complete
Digest: sha256:80f31da1ac7b312ba29d65080fddf797dd76acfb870e677f390d5acba9741b17
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:

1.  The Docker client contacted the Docker daemon.
2.  The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (arm64v8)
3.  The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
4.  The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
$ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
https://hub.docker.com/

For more examples and ideas, visit:
https://docs.docker.com/get-started/
```

命令`docker info`让我们检查 Docker。它会包含很多输出，但重点关注顶部的行，显示我们现在有 1 个已停止的容器和 1 个镜像。

```shell
$ docker info
Client:
Debug Mode: false

Server:
Containers: 1
Running: 0
Paused: 0
Stopped: 1
Images: 1
...
```

这意味着 Docker 已成功安装并运行。

## 2.5 安装 Django

现在我们将创建一个在本地计算机上运行的 Django "Hello, World"项目，然后将其完全移到 Docker 中（"Docker 化"），这样你就可以看到所有部分是如何组合在一起的。

你可以将 Django 代码保存在任何你喜欢的地方，但为了方便起见，我们将把代码放在桌面目录中。命令`cd`（更改目录）后跟预期位置在 Windows 和 macOS 计算机上都可以从命令行导航到桌面。

```shell
# Windows
$ cd onedrive\desktop
$ pwd

## Path
C:\Users\wsv\onedrive\desktop

# macOS
$ cd desktop
$ pwd
/Users/wsv/desktop
```

要创建新目录，请使用命令`mkdir`后跟名称。我们将在桌面上创建一个名为`code`的目录，然后在其中创建一个名为`ch2-hello`的新目录。

```shell
# Windows
$ mkdir code
$ cd code
$ mkdir ch2-hello
$ cd ch2-hello

# macOS
$ mkdir code
$ cd code
$ mkdir ch2-hello
$ cd ch2-hello
```

要在这个新目录中创建虚拟环境，在 Windows 上使用格式`python -m venv <name_of_env>`，在 macOS 上使用`python3 -m venv <name_of_env>`。创建后，必须激活虚拟环境。开发人员可以选择合适的环境名称，但常见的选择是称其为`.venv`。

在 Windows 上，必须设置执行策略以启用运行脚本。这是一种安全预防措施。Python 文档建议仅允许 CurrentUser 的脚本，这就是我们要做的。在 macOS 上，对脚本没有类似的限制，因此可以直接运行`source .venv/bin/activate`。

以下是创建和激活名为`.venv`的新虚拟环境的完整命令：

```shell
# Windows
$ python -m venv .venv
$ Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
$ .venv\Scripts\Activate.ps1

# macOS
$ python3 -m venv .venv
$ source .venv/bin/activate
```

虚拟环境激活后，命令行前缀将显示虚拟环境的名称，在我们的例子中是`(.venv)`。

```shell
(.venv) $
```

现在让我们安装 Django。

```shell
(.venv) $ python -m pip install django~=4.0.0
```

现在创建一个新的 Django 项目，我们将其称为`django_project`，并导航到其中。不要忘记在末尾添加句点`.`！

```shell
(.venv) $ django-admin startproject django_project .
```

> 注意：Django 4.0.x 版本与 Python 3.13 存在兼容性问题，核心原因为 Python 3.13 中移除了 cgi 模块，而此 Django 版本还依赖这个模块。
> 解决方法：升级 Django 版本到 4.2 +

让我们暂停一下，看看我们的文件结构是什么样的。

```shell
(.venv) $ ls
django_project  manage.py
```

现在让我们运行`migrate`来设置数据库并启动本地服务器。

```shell
(.venv) $ python manage.py migrate
(.venv) $ python manage.py runserver
```

导航到`http://127.0.0.1:8000/`查看熟悉的 Django 欢迎页面。

## 2.6 Pages 应用

现在让我们创建一个非常基本的 Django 应用，这样我们就有一些自定义代码可以使用。停止本地服务器`Control+c`并创建一个新的应用`pages`。

```shell
(.venv) $ python manage.py startapp pages
```

现在我们需要将新应用添加到`INSTALLED_APPS`配置中。使用你的文本编辑器打开`django_project/settings.py`文件并进行更新。

```python
# django_project/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pages",  # 新增
]
```

现在让我们创建我们的第一个网页，它将只是说"Hello, World"。首先更新`pages/views.py`文件。

```python
# pages/views.py
from django.http import HttpResponse

def home_page_view(request):
    return HttpResponse("Hello, World!")
```

然后创建一个`pages/urls.py`文件。

```python
# pages/urls.py
from django.urls import path
from .views import home_page_view

urlpatterns = [
    path("", home_page_view, name="home")
]
```

最后更新项目级别的`django_project/urls.py`文件。

```python
# django_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
]
```

现在启动本地服务器。

```shell
(.venv) $ python manage.py runserver
```

导航到`http://127.0.0.1:8000/`查看我们的"Hello, World"页面。

最后一步是创建一个 requirements.txt 文件，其中包含当前安装在我们虚拟环境中的所有 Python 包的记录。命令`pip freeze`将输出当前虚拟环境的内容，通过使用`>`操作符，我们可以一步完成：将内容输出到名为 requirements.txt 的新文件中。如果你的服务器仍在运行，请输入`Ctrl+c`和`Enter`退出，然后输入此命令。

```shell
(.venv) $ pip freeze > requirements.txt
```

将创建一个新的 requirements.txt 文件。它应该包含 Django 以及在安装 Django 时自动包含的包 asgiref 和 sqlparse。

```
asgiref==3.5.2
Django==4.0.4
sqlparse==0.4.2
```

现在是时候切换到 Docker 了。通过输入`deactivate`和回车退出我们的虚拟环境，因为我们不再需要它。

```shell
(.venv) $ deactivate
$
```

我们如何知道虚拟环境不再活跃？命令行提示符上的目录名称周围将不再有括号。此时你尝试运行的任何正常 Django 命令都会失败。例如，尝试`python manage.py runserver`看看会发生什么。

```shell
$ python manage.py runserver
...
ModuleNotFoundError: No module named 'django'
```

这意味着我们完全退出了虚拟环境，准备好使用 Docker 了。

## 2.7 Docker 镜像

Docker 镜像是描述如何创建 Docker 容器的只读模板。镜像是指令，而容器是镜像的实际运行实例。继续我们之前在本章中的公寓类比，镜像是建造公寓的蓝图或一套计划；容器是实际的、完全建成的建筑。

镜像通常基于另一个镜像，并进行一些额外的自定义。例如，根据所需的 Python 版本和风格，有一长串官方支持的 Python 镜像。

## 2.8 Dockerfile

对于我们的 Django 项目，我们需要创建一个包含 Python 但也安装我们的代码并具有额外配置详细信息的自定义镜像。要构建我们自己的镜像，我们创建一个名为 Dockerfile 的特殊文件，该文件定义创建和运行自定义镜像的步骤。

使用你的文本编辑器在项目级目录中的 manage.py 文件旁边创建一个新的 Dockerfile 文件。在其中添加以下代码，我们将在下面逐行解释。

```dockerfile
# 拉取基础镜像
FROM python:3.10.4-slim-bullseye

# 设置环境变量
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 设置工作目录
WORKDIR /code

# 安装依赖项
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# 复制项目
COPY . .
```

Dockerfile 在创建镜像时从上到下读取。第一个指令是`FROM`命令，它告诉 Docker 我们想要为应用程序使用什么基础镜像。Docker 镜像可以从其他镜像继承，所以我们不会创建自己的基础镜像，而是使用已经包含 Django 应用程序所需的所有工具和包的官方 Python 镜像。在这种情况下，我们使用 Python 3.10.4 和更小的 slim 变体，它不包含默认标签中包含的常见包。标签 bullseye 指的是最新的稳定 Debian 版本。明确设置这个是一个好主意，以最小化 Debian 新版本发布时的潜在破坏。

然后我们使用`ENV`命令设置三个环境变量：

- `PIP_DISABLE_PIP_VERSION_CHECK`禁用每次 pip 更新的自动检查
- `PYTHONDONTWRITEBYTECODE`意味着 Python 不会尝试写入.pyc 文件
- `PYTHONUNBUFFERED`确保我们的控制台输出不被 Docker 缓冲

命令`WORKDIR`用于在运行其余命令时设置默认工作目录。这告诉 Docker 使用此路径作为所有后续命令的默认位置。因此，我们可以使用基于工作目录的相对路径，而不是每次都输入完整的文件路径。在我们的例子中，工作目录是`/code`，但它通常可能更长，类似于`/app/src`、`/usr/src/app`或类似的变体，这取决于项目的具体需求。

下一步是使用 pip 和我们已经创建的 requirements.txt 文件安装我们的依赖项。`COPY`命令接受两个参数：第一个参数告诉 Docker 要将哪些文件复制到镜像中，第二个参数告诉 Docker 你希望文件被复制到哪里。在这种情况下，我们将现有的 requirements.txt 文件从本地计算机复制到当前工作目录，该目录由`.`表示。

一旦 requirements.txt 文件在镜像内部，我们可以使用最后一个命令`RUN`来执行 pip install。这与在本地机器上运行 pip install 完全相同，但这次模块被安装到镜像中。`-r`标志告诉 pip 打开一个文件——这里称为 requirements.txt——并安装其内容。如果我们不包含`-r`标志，pip 会尝试并失败安装 requirements.txt，因为它本身不是实际的 Python 包。

目前我们有一个基于 Python 3.10.4 的 slim-bullseye 变体的新镜像，并已安装了我们的依赖项。最后一步是将当前目录中的所有文件复制到镜像上的工作目录中。我们可以通过使用`COPY`命令来做到这一点。记住它接受两个参数，所以我们将本地文件系统上的当前目录（`.`）复制到镜像的工作目录（`.`）中。

如果你现在感到困惑，不要担心。Docker 有很多要吸收的内容，但好消息是"Docker 化"现有项目所涉及的步骤非常相似。

## 2.9 .dockerignore

`.dockerignore`文件是指定某些文件和目录不应包含在 Docker 镜像中的最佳实践方式。这可以帮助减少整体镜像大小，并通过将意图保密的内容排除在 Docker 之外来提高安全性。

目前我们可以安全地忽略本地虚拟环境（`.venv`）、我们未来的`.git`目录和`.gitignore`文件。在你的文本编辑器中，在现有 manage.py 文件旁边的基础目录中创建一个名为`.dockerignore`的新文件。

```
.venv
.git
.gitignore
```

我们现在有了创建自定义镜像的完整指令，但我们实际上还没有构建它。执行此操作的命令毫不奇怪地是`docker build`，后跟句点`.`，表示 Dockerfile 位于当前目录中。这里会有很多输出。我只包含了前两行和最后一行。

```shell
$ docker build .
[+] Building 9.1s (10/10) FINISHED
=> [internal] load build definition from Dockerfile
...
=> => writing image sha256:89ede1...
```

## 2.10 docker-compose.yml

我们完全构建的自定义镜像现在可以作为容器运行。为了运行容器，我们需要一个名为 docker-compose.yml 的文件中的指令列表。使用你的文本编辑器在项目级目录中的 Dockerfile 旁边创建一个 docker-compose.yml 文件。它将包含以下代码。

```yaml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "8000:8000"
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
```

在顶行，我们设置了 Docker Compose 的最新版本，目前是 3.9。然后我们指定我们希望在 Docker 主机中运行哪些服务（或容器）。可能有多个服务运行，但现在我们只有一个用于 web。

在 web 中，我们设置 build 在当前目录中查找我们的 Dockerfile。我们将使用 Django 默认端口 8000 并执行命令来运行本地 web 服务器。最后，volumes mount 自动将 Docker 文件系统与我们本地计算机的文件系统同步。这样，如果我们在 Docker 中对代码进行更改，它将自动与本地文件系统同步。

最后一步是使用命令`docker-compose up`运行我们的 Docker 容器。此命令将在命令行上产生另一长串输出代码。

```shell
$ docker-compose up
[+] Building .4s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
...
Attaching to docker-web-1
docker-web-1 | Watching for file changes with StatReloader
docker-web-1 | Performing system checks...
docker-web-1 |
docker-web-1 | System check identified no issues (0 silenced).
docker-web-1 | May 16, 2022 - 18:08:08
docker-web-1 | Django version 4.0.4, using settings 'django_project.settings'
docker-web-1 | Starting development server at http://0.0.0.0:8000/
docker-web-1 | Quit the server with CONTROL-C.
```

要确认它确实有效，请在 web 浏览器中返回`http://127.0.0.1:8000/`。刷新页面，"Hello, World"页面应该仍然出现。

Django 现在完全在 Docker 容器中运行。我们不在本地虚拟环境中工作。我们没有执行 runserver 命令。我们所有的代码现在都存在，我们的 Django 服务器在一个自包含的 Docker 容器中运行。成功！

在本书的过程中，我们将创建多个 Docker 镜像和容器，通过练习，流程将开始变得更有意义：

1. 创建一个带有自定义镜像指令的 Dockerfile
2. 添加一个.dockerignore 文件
3. 构建镜像
4. 创建一个 docker-compose.yml 文件
5. 启动容器

使用`Control+c`（同时按"Control"和"c"按钮）停止当前运行的容器，并另外输入`docker-compose down`。Docker 容器占用大量内存，所以当你使用完它们时停止它们是一个好主意。容器意味着是无状态的，这就是为什么我们使用 volumes 在本地复制我们的代码，在那里它可以被保存。

```shell
$ docker-compose down
[+] Running 2/0
⠿ Container docker-web-1 Removed
⠿ Network docker_default Removed
$
```

每当引入任何新技术时，都存在潜在的安全问题。在 Docker 的情况下，一个例子是它将默认用户设置为 root。root 用户（也称为"超级用户"或"管理员"）是 Linux 中用于系统管理的特殊用户帐户。它是 Linux 系统上最有特权的用户，可以访问所有命令和文件。

Docker 文档包含一个关于安全性的大部分，特别是关于 rootless 模式以避免这种情况。我们不会在这里涵盖它，因为这是一本关于 Django 的书，而不是 Docker，但特别是如果你的网站存储敏感信息，在上线之前请仔细查看整个安全部分。

## 2.11 Git

Git 是当今版本控制系统的选择，我们将在本书中使用它。使用`git init`初始化一个新的存储库，并运行`git status`查看哪些文件/目录将被跟踪。

```shell
$ git init
$ git status
```

在进行第一次提交之前，在项目根目录中创建一个`.gitignore`文件总是一个好主意。我们将包括我们的虚拟环境目录`.venv`、pycache 文件夹、本地数据库`db.sqlite3`，如果在 macOS 上还有`.DS_Store`。

```
.venv
**pycache**/
db.sqlite3
.DS_Store # 仅Mac
```

如果你再次运行`git status`，它应该显示以下内容：

```shell
$ git status
.......
```

数据库和虚拟环境都不被 Git 忽略。继续将所有当前文件添加到 Git 并创建我们的第一次提交和消息。

```shell
$ git add .
$ git commit -m 'ch2-hello'
```

你可以将本章的代码与 Github 上可用的官方存储库进行比较。

## 2.12 结论

Docker 是一个自包含的环境，包括我们本地开发所需的一切：web 服务、数据库，如果我们想要的话还有更多。与 Django 一起使用时，一般模式将始终相同：

1. 创建一个新的虚拟环境并安装 Django
2. 在其中创建一个新的 Django 项目
3. 编写 Dockerfile 并构建初始镜像
4. 编写 docker-compose.yml 文件并使用 docker-compose up 运行容器

我们将使用 Docker 构建更多 Django 项目，以便这个流程更有意义，但这就是全部内容。在下一章中，我们将使用 Docker 创建一个新的 Django 项目，并在单独的容器中添加 PostgreSQL 作为我们的数据库。
