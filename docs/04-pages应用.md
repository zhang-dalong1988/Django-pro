# Pages 应用

让我们为我们的新项目构建一个主页。目前，这将是一个静态页面，意味着它不会以任何方式与数据库交互。之后它将成为一个动态页面，用于展示可供销售的图书，但我们需要遵循"一次只做一件事"的原则，循序渐进地开发。

即使在一个成熟的项目中，通常也会有多个静态页面，比如"关于我们"、"联系我们"或"隐私政策"等页面，因此创建一个专门的`pages`应用来管理这些静态内容是一种良好的实践。接下来，让我们在命令行中使用`startapp`命令创建一个`pages`应用。

```bash
$ docker-compose exec web python manage.py startapp pages
```

然后将它添加到我们的`INSTALLED_APPS`设置中。我们还将更新`TEMPLATES`，使 Django 查找项目级别的`templates`文件夹。默认情况下，Django 会在每个应用中查找 templates 文件夹，但将所有模板组织在一个地方更容易管理。

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
    "pages.apps.PagesConfig",  # 新增
]

TEMPLATES = [
    {
        ...
        "DIRS": [BASE_DIR / "templates"],  # 新增
        ...
    }
]
```

请注意，更新`DIRS`设置意味着 Django 现在会同时查找这个新的项目级模板文件夹；同时它仍然会查找各个应用内部的 templates 文件夹。这种配置使我们能够更灵活地组织模板文件，既可以集中管理共用模板，也可以在各应用中保留特定功能的模板。

## 模板

在命令行中创建新的`templates`目录了。

```bash
$ mkdir templates
```

接下来，在此目录中创建两个新文件：`templates/_base.html`和`templates/home.html`。第一个文件是基础模板，将被所有其他模板继承；而`home.html`将作为我们网站的主页。

为何将基础模板命名为`_base.html`而非简单的`base.html`呢？这是一种编程风格的选择，许多开发者喜欢在那些仅用于被继承而不会直接渲染的模板文件名前加下划线`_`，使其在文件列表中更加醒目。

在基础模板中，我们将包含网页必需的基本结构，并设置`title`和`content`的`block`标签。这些块标签提供了模板继承的灵活性，允许子模板覆盖特定区域的内容。例如，每个页面都需要独特的标题显示在浏览器的`<title></title>`标签中，通过块标签，我们可以在每个继承模板中轻松定制这些内容。

为什么选择`content`作为主要内容区域的名称？虽然这个名称可以是任意的——比如`main`或其他描述性词汇——但在 Django 生态系统中，`content`已成为一种广泛接受的惯例。当然，你完全可以使用其他名称，但在阅读 Django 项目代码时，`content`无疑是你最常遇到的块名称。

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

现在是主页，目前它只会简单地显示"This is our home page."。

```html
<!-- templates/home.html -->
{% extends "_base.html" %} {% block title %}Home{% endblock title %} {% block
content %}
<h1>This is our home page.</h1>
{% endblock content %}
```

## URLs 和视图

在 Django 项目中，每个网页的呈现都需要模板、`urls.py`和`views.py`文件三者协同工作。对于初学者而言，这三个组件的配置顺序并非固定，但它们缺一不可。通常情况下，我们还需要第四个组件`models.py`来处理数据库交互，这种组件间的相互依赖关系可能会让新手感到些许困惑。就个人经验而言，我倾向于先配置 URL 路由，但在构建 Django 应用的过程中，实际上并不存在一个所谓的"标准工作流程"。

首先，我们从项目级别的`urls.py`文件入手，为`pages`应用中的页面设置合适的路由。由于我们正在创建网站的主页，因此 URL 路径不需要任何额外前缀，这通过空字符串`""`来实现。同时，我们在第二行引入`include`函数，这让我们能够以一种优雅且模块化的方式将`pages`应用的 URL 配置无缝整合到主项目的`urls.py`文件中。

```python
# django_project/urls.py
from django.contrib import admin
from django.urls import path, include  # new

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),  # new
]
```

接下来，我们需要创建`pages/urls.py`文件来配置应用级别的 URL 路由。在这个文件中，我们将导入之前定义的`HomePageView`视图，并将根路径（用空字符串`""`表示）映射到该视图。值得注意的是，我们在路径配置的末尾添加了一个名为`"home"`的[命名 URL](https://docs.djangoproject.com/zh-hans/5.2/topics/http/urls/#naming-url-patterns)。虽然这是可选的，但强烈推荐使用，因为命名 URL 能让我们在模板和视图中更灵活地引用路径，而不必担心 URL 结构的变化。这个命名 URL 的便利性很快就会在项目中体现出来。

```python
# pages/urls.py
from django.urls import path

from .views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]
```

最后，我们需要创建`views.py`文件来处理视图逻辑。在这里，我们可以充分利用 Django 内置的[TemplateView](https://docs.djangoproject.com/zh-hans/5.2/ref/class-based-views/base/#templateview)类，这是一个强大的通用视图，专为简单的模板渲染而设计。使用 TemplateView，我们只需指定`template_name`属性为`home.html`，Django 就会自动处理模板的加载和渲染过程，无需编写额外的逻辑代码。

```python
# pages/views.py
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "home.html"
```

我们几乎完成了。如果你现在导航到主页`http://127.0.0.1:8000/`，你可能会遇到一个错误。这是什么原因导致的呢？由于我们使用了`-d`标志在后台分离模式下运行容器，我们需要显式查看日志才能了解控制台输出的详细信息。

在终端中执行`docker-compose logs`命令，你会发现一个错误提示："ModuleNotFoundError: No module named 'pages.urls'"。这是因为 Django 不会根据我们的更改自动更新`django_project/settings.py`文件。在传统的非 Docker 环境中，只需停止并重启服务器就能解决这个问题，因为设置变量是在服务器启动时预加载的。在 Docker 环境中，我们也需要采取类似的操作，即先执行`docker-compose down`关闭容器，然后再执行`docker-compose up -d`重新启动，以确保新的`pages`应用被正确加载。

```bash
$ docker-compose down
$ docker-compose up -d
```

## 测试

现在，让我们为我们的应用添加测试。对于主页这种不涉及数据库操作的简单页面，Django 提供了[SimpleTestCase](https://docs.djangoproject.com/zh-hans/5.2/topics/testing/tools/#simpletestcase)类，它是标准`TestCase`的一个轻量级变体，专门针对不需要模型交互的视图进行优化。

虽然测试对初学者来说可能显得有些复杂，但随着实践的深入，你会发现测试工作往往遵循相似的模式和结构，变得相对直观和可预测。接下来，我们将修改`pages/tests.py`文件，首先从最基础的模板测试开始，确保我们的视图正确渲染。

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

首先，我们导入了`SimpleTestCase`类和[reverse](https://docs.djangoproject.com/zh-hans/5.2/ref/urlresolvers/#reverse)函数。`SimpleTestCase`是专为不需要数据库操作的测试场景设计的，而`reverse`函数则允许我们通过名称动态生成 URL，这在测试中非常实用。

接着，我们创建了一个名为`HomepageTests`的测试类，它继承自`SimpleTestCase`，并在其中定义了多个测试方法。每个测试方法都遵循 Python 的类方法约定，将`self`作为第一个参数——这是[Python 类设计的基本规范](https://docs.python.org/zh-cn/3/tutorial/classes.html#random-remarks)。

我们编写的两个测试方法都专注于验证主页是否正常响应（HTTP 状态码为`200`）。具体来说：

- `test_url_exists_at_correct_location`方法直接访问根 URL(`/`)，然后使用 Python 的[assertEqual](https://docs.python.org/zh-cn/3/library/unittest.html#unittest.TestCase.assertEqual)方法验证响应状态码是否为 200。
- `test_homepage_url_name`方法则通过`reverse`函数解析名为"home"的 URL（在`pages/urls.py`中定义），再进行访问测试。这种方式的优势在于，即使将来 URL 路径发生变化，只要名称保持不变，测试代码就无需修改。

执行这些测试

```bash
$ docker-compose exec web python manage.py test
```

你可能会疑惑：为什么测试结果显示有`4`个测试，而我们明明只编写了 2 个？这是因为当我们执行测试命令时，Django 默认会运行整个项目中的所有测试。在前一章中，我们已经在`users/tests.py`文件中为自定义用户模型创建了两个测试用例。如果你只想针对性地运行`pages`应用的测试，可以在测试命令后面指定应用名称，例如：`docker-compose exec web python manage.py test pages`。这样就能精确地只执行特定应用下的测试用例，提高测试效率。

## 测试模板

到目前为止，我们已经测试了主页是否存在，但我们也应该确认它使用了正确的模板。`SimpleTestCase`带有一个名为[assertTemplateUsed](https://docs.djangoproject.com/zh-hans/5.2/topics/testing/tools/#django.test.SimpleTestCase.assertTemplateUsed)的方法，专门用于此目的！

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

再次运行测试。

```bash
$ docker-compose exec web python manage.py test pages
```

你是否注意到这个命令的特别之处？我们在命令末尾指定了应用名称`pages`，这样系统就只会执行该应用内的测试用例。虽然在项目初期，运行全部测试并不会带来太大负担，但随着项目规模扩大，如果你明确知道只修改了特定应用的测试，有针对性地只运行这部分测试而非整个测试套件，可以显著提高开发效率和测试速度。这种精确控制测试范围的能力，是 Django 测试框架的一大优势。

## 测试 HTML

现在让我们进一步验证主页的 HTML 内容是否符合预期。编写测试时，不仅要测试预期成功的情况，也要测试预期失败的场景，这两种测试同样重要！通过这种双向验证，我们能更全面地确保页面内容的准确性和完整性。

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
```

## setUp()

你是否注意到我们在这些单元测试中存在重复代码？每个测试方法都需要加载一个`response`变量，这不仅冗余，还可能导致错误。遵循 DRY（Don't Repeat Yourself，不要重复自己）原则，我们可以在测试类顶部定义一个`setUp`方法，统一处理`response`变量的初始化。

通过这种改进，我们的`test_homepage_url_name`测试变得多余了，因为`setUp`方法已经使用`reverse("home")`获取了 URL 并存储了响应，所以我们可以安全地移除这个测试方法。这样既简化了代码结构，也提高了测试的可维护性。

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

运行测试

> 因为`setUp`是一个辅助方法，并且不以`test`开头，所以它不会被视为最终计数中的单元测试。因此，总共只会运行`6`个测试。

```bash
$ docker-compose exec web python manage.py test
```

## Resolve

我们可以进行的最后一个视图检查是验证我们的`HomePageView`能否正确"解析"给定的 URL 路径。Django 提供了一个名为[resolve](https://docs.djangoproject.com/zh-hans/5.2/ref/urlresolvers/#resolve)的实用函数，专门用于此目的。为了使用这个功能，我们需要在文件顶部导入`resolve`和`HomePageView`。

在我们的测试方法`test_homepage_url_resolves_homepageview`中，我们将检查当解析根路径`/`时，返回的视图函数名称是否与`HomePageView`的视图函数名称相匹配，从而确保 URL 配置正确指向了我们期望的视图。

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

运行测试

```bash
$ docker-compose exec web python manage.py test
```

## Git

是时候使用 Git 将我们的新更改添加到源代码控制中。

```bash
$ git status
$ git add .
$ git commit -m 'ch3-书店项目 pages 应用'
$ git push
```

## 小结

- 创建、安装/注册 Django 应用
- 配置项目级模板目录，以及基础模板 `_base.html` 的最佳实践
- 设置 URL 路由，包括项目级 urls.py 和应用级 urls.py 的配置
- 使用 TemplateView 类实现简单的视图逻辑
- 编写全面的测试用例，包括：
  - 测试 URL 是否存在并返回正确状态码
  - 测试是否使用了正确的模板
  - 测试页面内容是否包含预期的 HTML
  - 使用 setUp() 方法优化测试代码
  - 使用 resolve() 验证 URL 解析是否正确
