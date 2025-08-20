# 第 13 章：文件/图片上传

我们之前在第 6 章中配置了静态资源（如图片），但用户上传的文件（如书籍封面）有所不同。首先，Django 将前者称为静态资源（static），而用户上传的任何内容（无论是文件还是图片）都被称为媒体文件（media）。

为文件或图片添加此功能的过程类似，但对于图片，必须安装 Python 图像处理库 Pillow，它包含额外功能，如基本验证。

让我们使用我们现在熟悉的模式，将 pillow 添加到 requirements.txt 文件中进行安装。

```
# requirements.txt
asgiref==3.5.2
Django==4.0.4
psycopg2-binary==2.9.3
sqlparse==0.4.2
django-crispy-forms==1.14.0
crispy-bootstrap5==0.6
django-allauth==0.50.0
environs[django]==9.5.0
pillow==9.0.1
```

然后停止我们的 Docker 容器，重新构建 Docker 镜像，使其现在包含 pillow，然后再次启动容器。

```shell
$ docker-compose down
$ docker-compose up -d --build
```

## 媒体文件

从根本上讲，静态文件和媒体文件之间的区别在于我们可以信任前者，但默认情况下绝对不能信任后者。处理用户上传的内容时总是存在安全隐患。值得注意的是，验证所有上传的文件以确保它们是它们所声称的内容非常重要。恶意行为者可以通过多种恶劣方式攻击盲目接受用户上传的网站。

首先，让我们在 django_project/settings.py 文件中添加两个新配置。默认情况下，MEDIA_URL 和 MEDIA_ROOT 都是空的，不会显示，所以我们需要配置它们：

- MEDIA_ROOT 是用户上传文件的目录的绝对文件系统路径
- MEDIA_URL 是我们可以在模板中用于文件的 URL

我们可以在 django_project/settings.py 文件底部的 STATICFILES_STORAGE 之后添加这两个设置。我们将使用常见的约定，将两者都称为 media。不要忘记为 MEDIA_URL 包含尾部斜杠/！

```python
# django_project/settings.py

MEDIA_URL = "/media/" # new
MEDIA_ROOT = BASE_DIR / "media" # new
```

接下来，添加一个名为 media 的新目录和其中的一个名为 covers 的子目录。

```shell
$ mkdir media
$ mkdir media/covers
```

最后，由于假定用户上传的内容存在于生产环境中，要在本地查看媒体项目，我们需要更新 django_project/urls.py 以在本地显示文件。这涉及在顶部导入 settings 和 static，然后在底部添加一行。

```python
# django_project/urls.py

from django.conf import settings # new
from django.conf.urls.static import static # new
from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    # Django admin

    path("admin/", admin.site.urls),

    # User management

    path("accounts/", include("allauth.urls")),

    # Local apps

    path("", include("pages.urls")),
    path("books/", include("books.urls")),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
) # new
```

## 模型

完成通用媒体配置后，我们现在可以转向我们的模型。为了存储这些图像，我们将使用 Django 的 ImageField，它带有一些基本的图像处理验证功能。

字段名称为 cover，我们指定上传图像的位置将在 MEDIA_ROOT/covers 中（MEDIA_ROOT 部分是基于我们之前的 settings.py 配置隐含的）。

```python
# books/models.py

class Book(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    cover = models.ImageField(upload_to="covers/") # new

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book_detail", args=[str(self.id)])
```

如果我们想允许上传常规文件而不是图像文件，唯一的区别可能是将 ImageField 更改为 FileField。

由于我们已经更新了模型，现在是时候创建一个迁移文件了。

```shell
$ docker-compose exec web python manage.py makemigrations books
You are trying to add a non-nullable field 'cover_image' to book
without a default; we can't do that (the database needs something to populate
existing rows).
Please select a fix:

1.  Provide a one-off default now (will be set on all existing rows with a
    null value for this column)
2.  Quit, and let me add a default in models.py
    Select an option:
```

哎呀！发生了什么？我们正在添加一个新的数据库字段，但我们的数据库中已经有三个条目用于每本书。但我们没有为 cover 设置默认值。

要解决这个问题，输入 2 退出。我们将为现有图像添加一个设置为 True 的 blank 字段。

```python
# books/models.py

cover = models.ImageField(upload_to="covers/", blank=True) # new
```

通常会看到 blank 和 null 一起使用，为字段设置默认值。一个陷阱是字段类型——ImageField 与 CharField 等——决定了如何正确使用它们，所以请仔细阅读未来使用的文档。

现在我们可以创建一个没有错误的迁移文件。

```shell
$ docker-compose exec web python manage.py makemigrations books
Migrations for 'books':
  books/migrations/0003_book_cover.py - Add field cover to book
```

然后将迁移应用到我们的数据库。

```shell
$ docker-compose exec web python manage.py migrate
Operations to perform:
  Apply all migrations: account, accounts, admin, auth, books, contenttypes, sessions, si\
tes
Running migrations:
  Applying books.0003_book_cover... OK
```

## Admin

我们现在进入最后阶段！导航到管理界面和"Django for Professionals"书籍的条目。cover 字段已经可见，我们已经在 static/images/cover_40.jpg 本地有一个副本，所以使用该文件进行上传，然后点击右下角的"Save"按钮。

这将重定向回 Books 部分的主页。再次点击"Django for Professionals"的链接，我们可以看到它当前存在于我们所需的 covers/位置。

## 模板

好的，最后一步。让我们更新我们的模板，在每本书的个别页面上显示书籍封面。路径将是 book.cover.url，指向我们文件系统中封面的位置。

以下是更新后的 book_detail.html 文件，在标题上方添加了这一行更改。

```html
# templates/books/book_detail.html {% extends "_base.html" %} {% block title
%}{{ book.title }}{% endblock title %} {% block content %}

<div class="book-detail">
  <img class="bookcover" src="{{ book.cover.url}}" alt="{{ book.title }}" />
  <h2><a href="">{{ book.title }}</a></h2>
  <p>Author: {{ book.author }}</p>
  <p>Price: {{ book.price }}</p>
  <div>
    <h3>Reviews</h3>
    <ul>
      {% for review in book.reviews.all %}
      <li>{{ review.review }} ({{ review.author }})</li>
      {% endfor %}
    </ul>
  </div>
</div>
{% endblock content %}
```

如果你现在访问"Django for Professionals"的页面，你会看到封面图片自豪地展示在那里！

一个潜在的陷阱是我们的模板现在期望存在封面。如果你导航到其他两本书中的任何一本（我们尚未为其添加封面），你会看到以下相当描述性的 ValueError 消息。

我们必须在模板中添加一些基本逻辑，以便在不存在封面时模板不会寻找它！这可以通过使用 if 语句来完成，该语句检查 book.cover 并在存在时显示它。

```html
# templates/books/book_detail.html {% extends "_base.html" %} {% block title
%}{{ book.title }}{% endblock title %} {% block content %}

<div class="book-detail">
  {% if book.cover %}
  <img class="bookcover" src="{{ book.cover.url}}" alt="{{ book.title }}" />
  {% endif %}
  <h2><a href="">{{ book.title }}</a></h2>
  ...
</div>
```

如果你现在刷新任一书籍页面，你会看到它们显示正确的页面，尽管没有封面。

## django-storages

真正的生产网站可以采取几个步骤，但这些步骤超出了本书的当前范围。最重要的是将所有媒体文件存储在专用 CDN（内容分发网络）上，而不是在我们自己的服务器上。与开发人员控制并可以信任的静态文件不同，媒体文件是用户生成的，应始终谨慎对待。流行的第三方包 django-storages 允许将 Django 媒体文件存储在 Amazon 的 S3 等服务上。

此外，我们稍后将使用的托管服务 Heroku 具有临时文件系统。每个内部 dyno 都会从最近的部署中启动一个干净的文件系统副本。静态文件位于文件系统上；媒体文件不是。因此，在生产中，媒体文件不会保留在 Heroku 上。因此，在 Heroku 旁边使用 django-storages 基本上是强制性的，将在部署章节中再次提及。

## 下一步

额外的步骤可能包括对图像上传表单进行额外的验证，以确保只能添加正常、安全的图像。我们可以添加专用的创建/编辑/删除表单，用于创建书籍和封面图像。这里也最好有测试，尽管它们主要集中在表单验证部分，而不是通过管理界面进行基本图像上传。再次强调，这是一个可能变得相当复杂的领域，但值得进一步研究。

最后一个建议是查看第三方 django-cleanup 包，它可以自动删除旧文件。这可能非常方便。

## Git

确保为本章的更改创建一个新的 Git 提交。

```shell
$ git status
$ git add .
$ git commit -m 'ch13'
```

与往常一样，你可以将你的代码与 Github 上的官方源代码进行比较。

## 结论

本章演示了如何向项目添加用户文件。在实践中，这很简单，但额外的安全考虑层使其成为一个值得关注的领域。

在下一章中，我们将向我们的网站添加权限，以锁定它。
