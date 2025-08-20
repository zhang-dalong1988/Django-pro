# 第 11 章：Books 应用

在本章中，我们将为项目构建一个 Books 应用，用于显示所有可用的图书，并为每本书提供单独的页面。我们还将探索不同的 URL 方法，从使用 id 开始，然后切换到 slug，最后使用 UUID。

首先，我们必须创建这个新应用，我们将其命名为 books。

**Shell**

```bash
$ docker-compose exec web python manage.py startapp books
```

为确保 Django 知道我们的新应用，打开文本编辑器并将新应用添加到 django_project/settings.py 文件中的 INSTALLED_APPS：

```python
# django_project/settings.py

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # 第三方

    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",

    # 本地

    "accounts.apps.AccountsConfig",
    "pages.apps.PagesConfig",
    "books.apps.BooksConfig", # 新增
]
```

好的，初始创建完成！

## 11.1 模型

最终我们需要为每个页面创建模型、视图、URL 和模板，所以常常会讨论从哪里开始。模型是一个很好的起点，因为它设定了结构。让我们思考一下我们可能想要包含哪些字段。为了保持简单，我们将从标题（title）、作者（author）和价格（price）开始。

更新 books/models.py 文件以包含我们的新 Books 模型。

```python
# books/models.py

from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title
```

在顶部，我们导入了 Django 的 models 类，然后创建了一个继承它的 Book 模型，这意味着我们自动获得了 django.db.models.Model 中的所有功能，并且可以根据需要添加额外的字段和方法。

对于 title 和 author，我们将长度限制为 200 个字符，对于 price，我们使用 DecimalField，这在处理货币时是一个很好的选择。

下面我们指定了一个 **str** 方法来控制对象在 Admin 和 Django shell 中的输出方式。

现在我们的新数据库模型已创建，我们需要为其创建一个新的迁移记录。

**Shell**

```bash
$ docker-compose exec web python manage.py makemigrations
Migrations for 'books':
  books/migrations/0001_initial.py - Create model Book
```

然后将迁移应用到我们的数据库。

```bash
$ docker-compose exec web python manage.py migrate
Operations to perform:
  Apply all migrations: account, accounts, admin, auth, books, contenttypes, sessions, si\
tes
Running migrations:
  Applying books.0001_initial... OK
```

我们的数据库已配置好。让我们向管理员添加一些数据。

## 11.2 管理员

我们需要一种访问数据的方式，Django 管理员非常适合这个目的。别忘了更新 books/admin.py 文件，否则应用将不会出现！即使在使用 Django 多年后，我几乎每次都会忘记这一步。

```python
# books/admin.py

from django.contrib import admin

from .models import Book

admin.site.register(Book)
```

如果你查看 http://127.0.0.1:8000/admin/ 的管理员界面，Books 应用现在已经在那里了。

让我们为《Django for Professionals》添加一个图书条目。点击 Books 旁边的 + Add 按钮创建一个新条目。标题是"Django for Professionals"，作者是"William S. Vincent"，价格是$39.00。在金额中不需要包含美元符号 $，因为我们将在最终的模板中添加它。

点击"Save"按钮后，它会重定向到主 Books 页面，只显示标题。

让我们更新 books/admin.py 文件以指定我们还想显示哪些字段。

```python
# books/admin.py

from django.contrib import admin
from .models import Book

class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price",)

admin.site.register(Book, BookAdmin)
```

然后刷新页面。

现在我们的数据库模型已经完成，我们需要创建必要的视图、URL 和模板，以便在我们的 Web 应用程序中显示信息。从哪里开始总是一个问题，对开发人员来说也是一个令人困惑的问题。

个人而言，我通常从 URL 开始，然后是视图，最后是模板。

## 11.3 URL

我们需要更新两个 urls.py 文件。第一个是 django_project/urls.py。添加 books 应用的新路径。

```python
# django_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    # Django admin

    path("admin/", admin.site.urls),

    # User management

    path("accounts/", include("allauth.urls")),

    # Local apps

    path("", include("pages.urls")),
    path("books/", include("books.urls")), # 新增
]
```

现在在文本编辑器中为我们的 books 应用 URL 路径创建一个 books/urls.py 文件。我们将使用空字符串 ""，所以所有 books 应用的 URL 将基于刚刚在 django_project/urls.py 中设置的 URL 路径以 books/ 开头。它引用的视图 BookListView 尚未创建，它将具有 URL 名称 book_list。

```python
# books/urls.py

from django.urls import path

from .views import BookListView

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
]
```

## 11.4 视图

接下来是我们刚刚在 URL 文件中引用的 BookListView。这将依赖于内置的 ListView，这是 Django 为常见用例提供的通用类视图。我们只需要指定要使用的正确模型和模板。

```python
# books/views.py

from django.views.generic import ListView

from .models import Book

class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
```

注意模板 book_list.html 尚不存在。

## 11.5 模板

在我们的基础级模板目录中创建一个特定于应用的文件夹是可选的，但它可以提供帮助，特别是随着数量的增长，所以我们将创建一个名为 books 的文件夹。

**Shell**

```bash
$ mkdir templates/books/
```

在文本编辑器中创建一个名为 templates/books/book_list.html 的新文件。

```html
<!-- templates/books/book_list.html -->

{% extends "_base.html" %} {% block title %}Books{% endblock title %} {% block
content %} {% for book in object_list %}

<div>
  <h2><a href="">{{ book.title }}</a></h2>
</div>
{% endfor %} {% endblock content %}
```

在顶部，我们注明此模板扩展了 \_base.html，然后用内容块包装我们想要的代码。我们使用 Django 模板语言为每本书设置一个简单的 for 循环。注意，object_list 来自 ListView，包含视图中的所有对象。

最后一步是关闭然后重新启动我们的容器，以重新加载 Django django_project/settings.py 文件。否则，它不会意识到我们已经做了更改，因此会出现错误页面，日志中会有关于 "ModuleNotFoundError: No module named 'books.urls'" 的消息。

关闭然后重新启动我们的容器。

**Shell**

```bash
$ docker-compose down
$ docker-compose up -d
```

在你的网络浏览器中访问 http://127.0.0.1:8000/books/ 可以看到新的图书页面。

## 11.6 object_list

正如我们刚刚看到的，ListView 依赖于 object_list，但这远非描述性。更好的方法是使用 context_object_name 将其重命名为更友好的名称。

按如下方式更新 books/views.py。

```python
# books/views.py

from django.views.generic import ListView

from .models import Book

class BookListView(ListView):
    model = Book
    context_object_name = "book_list" # 新增
    template_name = "books/book_list.html"
```

然后在我们的模板中将 object_list 替换为 book_list。

```html
<!-- templates/books/book_list.html -->

{% extends "_base.html" %} {% block title %}Books{% endblock title %} {% block
content %} {% for book in book_list %}

<div>
  <h2><a href="">{{ book.title }}</a></h2>
</div>
{% endfor %} {% endblock content %}
```

刷新页面，它仍然像以前一样工作！这种技术在大型项目中特别有用，多个开发人员在一个项目上工作。前端工程师很难正确猜测 object_list 的含义！

为了证明列表视图适用于多个项目，通过管理员向网站添加两本更多的书。我添加了我的另外两本 Django 书籍——《Django for APIs》和《Django for Beginners》，它们都以"William S. Vincent"为作者，价格为"39.00"。

## 11.7 单本图书页面

现在我们可以通过使用另一个名为 DetailView 的通用类视图为每本书添加单独的页面。

我们的过程类似于 Books 页面，从 URL 开始，在第二行导入 BookDetailView，然后设置路径为每本书的主键，它将表示为整数 <int:pk>。

```python
# books/urls.py

from django.urls import path

from .views import BookListView, BookDetailView # 新增

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("<int:pk>/", BookDetailView.as_view(), name="book_detail"), # 新增
]
```

Django 自动为我们的数据库模型添加一个自动递增的主键。所以虽然我们只声明了 title、author 和 body 字段在我们的 Book 模型上，但在底层 Django 还添加了另一个名为 id 的字段，这是我们的主键。我们可以将其作为 id 或 pk 访问。

我们第一本书的 pk 是 1。第二本将是 2。依此类推。因此，当我们访问第一本书的单独条目页面时，我们可以预期其 URL 路由将是 books/1。

现在转到 books/views.py 文件，我们将导入 DetailView 并创建一个 BookDetailView 类，该类还指定了 model 和 template_name 字段。

```python
# books/views.py

from django.views.generic import ListView, DetailView # 新增

from .models import Book

class BookListView(ListView):
    model = Book
    context_object_name = "book_list"
    template_name = "books/book_list.html"

class BookDetailView(DetailView): # 新增
    model = Book
    template_name = "books/book_detail.html"
```

最后创建新的模板文件 templates/books/book_detail.html。它将显示所有当前字段。我们还可以在标题标签中展示标题，使其显示在网络浏览器标签中。

```html
<!-- templates/books/book_detail.html -->

{% extends "_base.html" %} {% block title %}{{ object.title }}{% endblock title
%} {% block content %}

<div class="book-detail">
  <h2><a href="">{{ object.title }}</a></h2>
  <p>作者: {{ object.author }}</p>
  <p>价格: {{ object.price }}</p>
</div>
{% endblock content %}
```

在你的网络浏览器中导航到 http://127.0.0.1:8000/books/1/ 你将看到我们第一本书的专用页面。

## 11.8 context_object_name

就像 ListView 默认为 object_list 一样，我们更新为更具体的名称，DetailView 默认为 object，我们可以使用 context_object_name 使其更具描述性。我们将其设置为 book。

```python
# books/views.py

...
class BookDetailView(DetailView):
    model = Book
    context_object_name = "book" # 新增
    template_name = "books/book_detail.html"
```

别忘了用这个更改更新我们的模板，将我们三个字段的 object 替换为 book。

```html
<!-- templates/books/book_detail.html -->

{% extends "_base.html" %} {% block title %}{{ book.title }}{% endblock title %}
{% block content %}

<div class="book-detail">
  <h2><a href="">{{ book.title }}</a></h2>
  <p>作者: {{ book.author }}</p>
  <p>价格: {{ book.price }}</p>
</div>
{% endblock content %}
```

## 11.9 添加 URL

我们希望图书列表页面上的链接指向单独的页面。使用 url 模板标签，我们可以指向 book_detail - 在 books/urls.py 中设置的 URL 名称 - 然后传入 pk。

```html
<!-- templates/books/book_list.html -->

{% extends "_base.html" %} {% block title %}Books{% endblock title %} {% block
content %} {% for book in book_list %}

<div>
  <h2><a href="{% url 'book_detail' book.pk %}">{{ book.title }}</a></h2>
</div>
{% endfor %} {% endblock content %}
```

刷新 http://127.0.0.1:8000/books/ 的图书列表页面，链接现在都可以点击，并指向正确的单独图书页面。

作为最后一步，让我们为"Books"添加一个导航栏链接，这样我们就不必每次都输入完整的 URL。我们的图书列表视图的 URL 名称 book_list 可以与 url 模板标签一起使用来实现这一点。以下是 templates/\_base.html 中更新的代码。

```html
<!-- templates/_base.html -->

...

<div class="collapse navbar-collapse" id="navbarCollapse">
  <ul class="navbar-nav me-auto mb-2 mb-md-0">
    <li class="nav-item">
      <a class="nav-link" href="{% url 'book_list' %}">Books</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{% url 'about' %}">About</a>
    </li>
    ...
  </ul>
</div>
```

刷新网站上的任何页面，工作的"Books"导航栏链接现在就在那里。

## 11.10 get_absolute_url

我们尚未做的一个推荐步骤是添加一个 get_absolute_url() 方法，它为模型设置一个规范 URL。当使用 reverse() 函数时，它也是必需的。

以下是如何将其添加到我们的 books/models.py 文件中。在顶部导入 reverse。然后添加 get_absolute_url 方法，它将是我们的 URL 名称 book_detail 的反向，并将 id 作为字符串传入。

```python
# books/models.py

from django.db import models
from django.urls import reverse # 新增

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title

    def get_absolute_url(self):  # 新增
        return reverse("book_detail", args=[str(self.id)])
```

然后我们可以更新模板。目前我们的 a href 链接使用 {% url 'book_detail' book.pk %}。但是我们可以直接使用 get_absolute_url，它已经传入了 pk。

```html
<!-- templates/books/book_list.html -->

{% extends '_base.html' %} {% block title %}Books{% endblock title %} {% block
content %} {% for book in book_list %}

<div>
  <h2><a href="{{ book.get_absolute_url }}">{{ book.title }}</a></h2>
</div>
{% endfor %} {% endblock content %}
```

现在不需要为链接使用 url 模板标签。相反，在 books/models.py 文件中有一个规范引用。这是一种更干净的方法，当你需要对象的单独页面时应该使用它。

## 11.11 主键与 ID

在项目中使用主键（PK）还是 ID 可能会令人困惑，特别是因为 Django 的 DetailView 将它们互换处理。但是有一个微妙的区别。

id 是 Django 内部自动设置的模型字段，用于自动递增。所以第一本书的 id 是 1，第二个条目是 2，依此类推。这也是默认情况下被视为模型的主键 pk。

然而，可以手动更改模型的主键是什么。它不必是 id，而可以是类似 object_id 的东西，取决于用例。此外，Python 有一个内置的 id() 对象，有时会导致混淆和/或错误。

相比之下，主键 pk 指的是模型的主键字段，所以当有疑问时使用 pk 更安全。事实上，在下一节中，我们将更新我们模型的 id！

## 11.12 Slugs 与 UUIDs

在我们的 DetailView 的 URL 中使用 pk 字段是快速且简单的，但对于真实世界的项目来说并不理想。pk 目前与我们的自动递增 id 相同。除了其他问题外，它告诉潜在的黑客你的数据库中有多少记录；它告诉他们确切的 id 是什么，可以在潜在的攻击中使用；如果你有多个前端，可能会有同步问题。

有两种替代方法。第一种称为"slug"，这是报纸术语，指的是用于 URL 中的东西的简短标签。例如，在我们的"Django for Professionals"示例中，它的 slug 可以是 django-for-professionals。甚至有一个 SlugField 模型字段可以使用，可以在创建标题字段时手动添加，也可以在保存时自动填充。使用 slug 的主要挑战是处理重复，尽管这可以通过向给定的 slug 字段添加随机字符串或数字来解决。但同步问题仍然存在。

更好的方法是使用 UUID（通用唯一标识符），Django 现在通过专用的 UUIDField 支持它。

让我们现在实现一个 UUID，通过向我们的模型添加一个新字段，然后更新 URL 路径。

在顶部导入 uuid，然后更新 id 字段实际上是一个 UUIDField，现在是主键。我们还使用 uuid4 进行加密。这允许我们使用 DetailView，它需要一个 slug 或 pk 字段；没有重大修改，它不会与 UUID 字段一起工作。

```python
# books/models.py

import uuid # 新增
from django.db import models
from django.urls import reverse

class Book(models.Model):
    id = models.UUIDField( # 新增
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book_detail", args=[str(self.id)])
```

在 URL 路径中，将详细视图中的 int 替换为 uuid。

```python
# books/urls.py

from django.urls import path

from .views import BookListView, BookDetailView

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("<uuid:pk>", BookDetailView.as_view(), name="book_detail"), # 新增
]
```

但现在我们面临一个问题：有现有的图书条目，实际上有三个，它们有自己的 id 以及使用它们的相关迁移文件。像这样创建一个新的迁移会导致真正的问题。最简单的方法，我们将使用，也是最具破坏性的：简单地删除旧的 books 迁移并重新开始。

```bash
$ docker-compose exec web rm -r books/migrations
$ docker-compose down
```

最后一个问题是，我们还通过卷挂载持久化我们的 PostgreSQL 数据库，它仍然有指向旧 id 字段的记录。你可以使用 docker volume ls 命令看到这一点。

```bash
$ docker volume ls
DRIVER VOLUME NAME
local books_postgres_data
```

最简单的方法再次是简单地删除卷并使用 Docker 重新开始。由于我们在项目的早期阶段，我们将采取这种方式；一个更成熟的项目将需要考虑一种更复杂的方法。

步骤包括启动我们的 web 和 db 容器；为 books 应用添加一个新的初始迁移文件，用 migrate 应用所有更新，然后再次创建一个超级用户账户。

```bash
$ docker volume rm books_postgres_data
$ docker-compose up -d
$ docker-compose exec web python manage.py makemigrations books
$ docker-compose exec web python manage.py migrate
$ docker-compose exec web python manage.py createsuperuser
```

现在进入管理员并再次添加三本书。如果你然后导航到主图书页面并点击一个单独的图书，你将被带到一个带有 URL 中的 UUID 的新详细页面。

通过删除卷，我们也失去了各种测试用户账户，但没关系。我们可以根据需要在未来重新创建它们。

## 11.13 测试

现在我们需要测试我们的模型和视图。我们希望确保 Books 模型按预期工作，包括其 str 表示。我们还想测试 ListView 和 DetailView。以下是 books/tests.py 文件中的示例测试。

```python
# books/tests.py

from django.test import TestCase
from django.urls import reverse

from .models import Book

class BookTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.book = Book.objects.create(
            title="Harry Potter",
            author="JK Rowling",
            price="25.00",
        )

    def test_book_listing(self):
        self.assertEqual(f"{self.book.title}", "Harry Potter")
        self.assertEqual(f"{self.book.author}", "JK Rowling")
        self.assertEqual(f"{self.book.price}", "25.00")

    def test_book_list_view(self):
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harry Potter")
        self.assertTemplateUsed(response, "books/book_list.html")

    def test_book_detail_view(self):
        response = self.client.get(self.book.get_absolute_url())
        no_response = self.client.get("/books/12345/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "Harry Potter")
        self.assertTemplateUsed(response, "books/book_detail.html")
```

我们导入 TestCase 并引入 setUpTestData 方法来添加一个示例书籍进行测试。使用 setUpTestData 通常会显著提高测试速度，因为初始数据是一次性创建的，而不是每个单元测试都创建一次。

第一个单元测试 test_book_listing 检查其字符串表示和内容是否正确。然后我们使用 test_book_list_view 确认我们的主页返回 200 HTTP 状态码，包含我们的正文文本，并使用正确的 books/book_list.html 模板。最后，test_book_detail_view 测试我们的详细页面按预期工作，并且不正确的页面返回 404。在你的测试中，测试某些东西确实存在和某些不正确的东西不存在总是好的。

现在运行这些测试。它们应该都通过。

**Shell**

```bash
$ docker-compose exec web python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................

----------------------------------------------------------------------

Ran 17 tests in 0.208s

OK
Destroying test database for alias 'default'...
```

## 11.14 Git

我们在本章中做了很多工作，所以现在通过 Git 添加到版本控制中，添加新文件并添加提交消息。

**Shell**

```bash
$ git status
$ git add .
$ git commit -m 'ch11'
```

本章的官方源代码可在 Github 上获取以供参考。

## 11.15 结论

我们已经到了相当长的一章的结尾，但我们书店项目的架构现在更加清晰。我们添加了一个图书模型，学习了如何更改 URL 结构，并切换到更安全的 UUID 模式。

在下一章中，我们将学习外键关系，并为我们的项目添加评论选项。
