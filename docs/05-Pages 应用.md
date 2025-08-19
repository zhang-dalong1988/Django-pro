# 第 5 章：Pages 应用

让我们为新项目构建一个主页。目前这将是一个静态页面，意味着它不会以任何方式与数据库交互。稍后它将成为一个显示待售书籍的动态页面，但是...一步一步来。

即使在成熟的项目中，拥有多个静态页面（如关于页面）也是很常见的，所以让我们为它们创建一个专门的 pages 应用。在命令行中再次使用 `startapp` 命令来创建一个 pages 应用。

## 1. 创建 Pages 应用

```bash
$ docker-compose exec web python manage.py startapp pages
```

然后将其添加到我们的 `INSTALLED_APPS` 设置中。我们还将更新 `TEMPLATES`，以便 Django 查找项目级别的 templates 文件夹。默认情况下，Django 在每个应用中查找 templates 文件夹，但将所有模板组织在一个空间中更容易管理。

```python
# django_project/settings.py

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local
    "accounts.apps.AccountsConfig",
    "pages.apps.PagesConfig",  # new
]

TEMPLATES = [
    {
        ...
        "DIRS": [BASE_DIR / "templates"],  # new
        ...
    }
]
```

请注意，更新 `DIRS` 设置意味着 Django 也会在这个新文件夹中查找；它仍然会查找应用内的任何 templates 文件夹。

## 2. 模板配置

接下来是时候在命令行中创建新的 templates 目录了。

```bash
$ mkdir templates
```

然后使用文本编辑器在其中创建两个新文件：`templates/_base.html` 和 `templates/home.html`。第一个基础级别文件将被所有其他文件继承；`home.html` 将是我们的主页。

为什么将基础模板称为 `_base.html` 而不是 `base.html`？这是一个可选的做法，但一些开发者更喜欢在仅用于被其他文件继承的文件前添加下划线 `_`。

在基础文件中，我们将包含所需的最少内容，并为 title 和 content 添加块标签。块标签为更高级别的模板提供了仅覆盖标签内内容的选项。例如，主页将有一个"Home"标题，但我们希望它出现在 HTML `<title></title>` 标签之间。使用块标签可以更容易地在继承的模板中根据需要更新此内容。

为什么使用 `content` 作为项目主要内容的名称？这个名称可以是任何东西——`main` 或其他通用指示符——但使用 `content` 是 Django 世界中的常见命名约定。你可以使用其他名称吗？当然可以。`content` 是你最常见到的吗？是的。

```html
<!-- templates/_base.html -->
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>{% block title %}Bookstore{% endblock title %}</title>
  </head>
  <body>
    <div class="container">{% block content %} {% endblock content %}</div>
  </body>
</html>
```

现在是主页，目前只会显示"This is our home page."。

```html
<!-- templates/home.html -->

{% extends "_base.html" %} {% block title %}Home{% endblock title %} {% block
content %}
<h1>This is our home page.</h1>
{% endblock content %}
```

## 3. URLs 和 Views 配置

Django 项目中的每个网页都需要一个 `urls.py` 和 `views.py` 文件来配合模板。对于初学者来说，这里的顺序实际上并不重要——我们需要所有 3 个文件，通常还需要第 4 个文件 `models.py` 用于数据库——这是令人困惑的。通常我更喜欢从 URLs 开始，然后从那里开始工作，但没有"正确的方式"来构建这个相互连接的 Django 文件网络。

让我们从项目级别的 `urls.py` 开始，为 pages 应用内的网页设置正确的路径。由于我们想创建一个主页，我们不在 URL 路由中添加额外的前缀，这由空字符串 `""` 指定。我们还在第二行导入 `include`，以简洁地将 pages 应用添加到我们的主 `urls.py` 文件中。

```python
# django_project/urls.py

from django.contrib import admin
from django.urls import path, include  # new

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),  # new
]
```

接下来我们使用文本编辑器创建一个 `pages/urls.py` 文件。这个文件将导入 `HomePageView` 并再次将路径设置为空字符串 `""`。请注意，我们在最后提供了一个可选但推荐的命名 URL `"home"`。这很快就会派上用场。

```python
# pages/urls.py

from django.urls import path

from .views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]
```

最后我们需要一个 `views.py` 文件。我们可以利用 Django 的内置 `TemplateView`，这样唯一需要调整的就是指定我们想要的模板 `home.html`。

```python
# pages/views.py

from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = "home.html"
```

我们快完成了。如果你现在导航到主页 `http://127.0.0.1:8000/`，你实际上会看到一个错误。但是什么导致了这个错误？由于我们在后台分离模式下运行容器——那个 `-d` 标志——我们必须明确检查日志以查看控制台输出。

在 shell 中输入 `docker-compose logs`，这将显示一个错误"ModuleNotFoundError: No module named 'pages.urls'"。发生的情况是 Django 不会根据更改自动为我们更新 `django_project/settings.py` 文件。在非 Docker 环境中，停止并重新启动服务器就可以解决问题，因为设置变量是预先加载的。我们必须在这里做同样的事情，这意味着输入 `docker-compose down` 然后 `docker-compose up -d` 来正确加载新的 pages 应用。

```bash
$ docker-compose down
$ docker-compose up -d
```

现在刷新主页，它将正常工作。

## 4. 测试

是时候进行测试了。对于我们的主页，我们可以使用 Django 的 `SimpleTestCase`，这是 Django 的 `TestCase` 的一个特殊子集，专为不包含模型的网页设计。

测试一开始可能会让人感到不知所措，但很快就会变得有点无聊。你会一遍又一遍地使用相同的结构和技术。在文本编辑器中，更新现有的 `pages/tests.py` 文件。我们将从测试模板开始。

```python
# pages/tests.py

from django.test import SimpleTestCase
from django.urls import reverse

class HomepageTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_homepage_url_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
```

在顶部我们导入 `SimpleTestCase` 以及 `reverse`，这对测试我们的 URLs 很有用。然后我们创建一个名为 `HomepageTests` 的类，它扩展了 `SimpleTestCase`，并在其中为每个单元测试添加一个方法。

请注意，我们将 `self` 作为每个单元测试的第一个参数添加。这是一个值得重复的 Python 约定。

最好对单元测试名称过度描述，但要注意每个方法必须以 `test` 开头才能被 Django 测试套件运行。

这里的两个测试都检查主页的 HTTP 状态码是否等于 200，这意味着它存在。它还没有告诉我们关于页面内容的任何具体信息。对于 `test_url_exists_at_correct_location`，我们创建一个名为 `response` 的变量，它访问主页（`/`），然后使用 Python 的 `assertEqual` 检查状态码是否匹配 200。`test_homepage_url_name` 存在类似的模式，除了我们通过 `reverse` 方法调用 URL 名称 `home`。回想一下，我们将此作为最佳实践添加到 `pages/urls.py` 文件中。即使我们将来更改此页面的实际路由，我们仍然可以通过相同的 `home` URL 名称引用它。

要运行我们的测试，请执行以 `docker-compose exec web` 为前缀的命令，以便它在 Docker 内部运行。

```bash
$ docker-compose exec web python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..

----------------------------------------------------------------------
Ran 4 tests in 0.126s

OK
Destroying test database for alias 'default'...
```

为什么说运行了 4 个测试，而我们只创建了 2 个？因为我们正在测试整个 Django 项目，在前一章的 `users/tests.py` 下，我们为自定义用户模型添加了两个测试。如果我们只想运行 pages 应用的测试，我们只需在命令后附加该名称，如 `docker-compose exec web python manage.py test pages`。

### 4.1 测试模板

到目前为止，我们已经测试了主页存在，但我们也应该确认它使用了正确的模板。`SimpleTestCase` 带有一个专门用于此目的的方法 `assertTemplateUsed`！让我们使用它。

```python
# pages/tests.py

from django.test import SimpleTestCase
from django.urls import reverse

class HomepageTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_homepage_url_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_homepage_template(self):  # new
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")
```

我们再次创建了一个 `response` 变量，然后检查是否使用了模板 `home.html`。让我们再次运行测试。

```bash
$ docker-compose exec web python manage.py test pages
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...

----------------------------------------------------------------------
Ran 3 tests in 0.009s

OK
Destroying test database for alias 'default'...
```

你注意到那个命令中有什么不同吗？我们添加了应用名称 `pages`，这样只运行该应用内的测试。在这个早期阶段运行所有测试是可以的，但在较大的项目中，如果你知道你只在特定应用内添加了测试，只运行更新/新的测试而不是整个套件可以节省时间。

### 4.2 测试 HTML

现在让我们确认我们的主页有正确的 HTML 代码，并且没有不正确的文本。测试通过的测试和我们期望失败的测试确实失败，这总是好的！

```python
# pages/tests.py

from django.test import SimpleTestCase
from django.urls import reverse

class HomepageTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_homepage_url_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_homepage_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_homepage_contains_correct_html(self):  # new
        response = self.client.get("/")
        self.assertContains(response, "home page")

    def test_homepage_does_not_contain_incorrect_html(self):  # new
        response = self.client.get("/")
        self.assertNotContains(response, "Hi there! I should not be on the page.")
```

再次运行测试。

```bash
$ docker-compose exec web python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.....

----------------------------------------------------------------------
Ran 7 tests in 0.279s

OK
Destroying test database for alias 'default'...
```

## 5. setUp() 方法

你有没有注意到我们在这些单元测试中似乎在重复自己？对于每一个，我们都在加载一个 `response` 变量，这似乎是浪费的并且容易出错。最好坚持更 DRY（Don't Repeat Yourself）的做法，比如在测试顶部用一个名为 `setUp` 的函数做一次，将响应加载到一个 `response` 变量中。

我们当前的 `test_homepage_url` 测试现在是多余的，因为 `setUp` 首先在我们命名的模板 `"home"` 上运行 `reverse`，所以我们可以删除该测试。

```python
# pages/tests.py

from django.test import SimpleTestCase
from django.urls import reverse

class HomepageTests(SimpleTestCase):
    def setUp(self):  # new
        url = reverse("home")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, "home.html")

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, "home page")

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")
```

现在再次运行测试。因为 `setUp` 是一个辅助方法，不以 `test` 开头，所以它不会被认为是最终统计中的单元测试。所以总共只会运行 6 个测试。

```bash
$ docker-compose exec web python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
....

----------------------------------------------------------------------
Ran 6 tests in 0.126s

OK
Destroying test database for alias 'default'...
```

## 6. Resolve 测试

我们可以做的最后一个视图检查是我们的 `HomePageView` "解析"给定的 URL 路径。Django 包含实用函数 `resolve` 正是为了这个目的。我们需要在文件顶部导入 `resolve` 以及 `HomePageView`。

我们的实际测试 `test_homepage_url_resolves_homepageview` 检查用于解析 `/` 的视图名称是否与 `HomePageView` 匹配。

```python
# pages/tests.py

from django.test import SimpleTestCase
from django.urls import reverse, resolve  # new

from .views import HomePageView  # new

class HomepageTests(SimpleTestCase):
    def setUp(self):
        url = reverse("home")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, "home.html")

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, "home page")

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi there! I should not be on the page.")

    def test_homepage_url_resolves_homepageview(self):  # new
        view = resolve("/")
        self.assertEqual(view.func.__name__, HomePageView.as_view().__name__)
```

呼。这是我们的最后一个测试。让我们确认一切都通过了。

```bash
$ docker-compose exec web python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.....

----------------------------------------------------------------------
Ran 7 tests in 0.126s

OK
Destroying test database for alias 'default'...
```

## 7. Git 版本控制

是时候使用 Git 将我们的新更改添加到源代码控制中了。

```bash
$ git status
$ git add .
$ git commit -m 'ch5'
```

你可以在 Github 上比较本章的官方源代码。

## 8. 总结

我们已经配置了模板并向项目添加了第一个页面，一个静态主页。我们还添加了测试，这应该始终包含在新的代码更改中。一些开发者更喜欢一种叫做测试驱动开发的方法，他们先编写测试，然后编写代码。个人而言，我更喜欢在之后立即编写测试，这就是我们在这里要做的。

两种方法都有效，关键是要严格进行测试。Django 项目的规模很快就会增长，在那里不可能记住你脑海中的所有工作部分。如果你在一个团队中工作，在一个未经测试的代码库上工作是一场噩梦。谁知道什么会坏掉？

在下一章中，我们将向项目添加用户注册：登录、注销和注册。
