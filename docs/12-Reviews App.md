# 第 12 章：评论应用

在本章中，我们将添加一个评论应用，让读者可以对他们喜欢的书籍发表评论。这给了我们一个机会来讨论外键、应用结构以及深入了解表单。

## 外键

我们已经在用户模型中使用了外键，但没有必要去思考它。现在我们需要了解！从根本上讲，数据库表可以被视为类似于具有行和列的电子表格。需要有一个主键字段，该字段是唯一的并且引用每条记录。在上一章中，我们将其从 id 更改为 UUID，但它仍然存在！

当我们想要链接两个表时，这一点很重要。例如，我们的 Books 模型将链接到 Reviews 模型，因为每条评论都必须与相关书籍相连。这意味着存在外键关系。

外键关系可能有三种类型：

- 一对一
- 一对多
- 多对多

一对一关系是最简单的类型。例如，人名表和社会安全号码表。每个人只有一个社会安全号码，每个社会安全号码只链接到一个人。

在实践中，一对一关系很少见。关系的两边都只与一个对应方匹配的情况很少见。其他一些例子包括国家-国旗或人-护照。

一对多关系更为常见，是 Django 中的默认外键设置。例如，考虑一家餐厅，一个顾客可以下多个订单。

也可以有 ManyToManyField 关系。让我们考虑一个书籍列表和一个作者列表：每本书可以有多个作者，每个作者可以写多本书。这是一个多对多关系。与前两个例子一样，您需要一个链接的外键字段来连接两个列表。其他例子包括医生和患者（每个医生看多个患者，反之亦然）或员工和任务（每个员工有多个任务，而每个任务由多个员工完成）。

数据库设计是一个既是艺术又是科学的迷人而深入的话题。随着项目中表的数量随着时间的推移而增长，几乎不可避免地需要进行重构，以解决围绕低效、臃肿和彻底错误的问题。规范化是构建关系数据库的过程，但这远远超出了本书的范围。

## Reviews 模型

回到我们的基本评论应用，首先要考虑的是将有什么类型的外键关系。如果我们要将用户链接到评论，那么这是一个简单的一对多关系。但是，也可以将书籍链接到评论，这将是多对多关系。"正确"的选择很快变得有些主观，当然取决于项目的特定需求。

在这个项目中，我们将把评论应用视为作者和评论之间的一对多关系，因为这是更简单的方法。

在这里，我们再次面临如何设计项目的选择。我们是在现有的 books/models.py 文件中添加 Reviews 模型，还是创建一个专门的 reviews 应用，然后将其链接起来？让我们首先在 books 应用中添加 Reviews 模型。

```python
# books/models.py

import uuid
from django.contrib.auth import get_user_model # new
from django.db import models
from django.urls import reverse

class Book(models.Model):
...

class Review(models.Model): # new
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    review = models.CharField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.review
```

在顶部，在导入下包含 get_user_model，这是引用我们的 CustomUser 模型所必需的，然后创建一个专用的 Review 模型。book 字段是将 Book 链接到 Review 的一对多外键，我们遵循标准做法，将其命名为与链接模型相同的名称。review 字段包含实际内容，根据您想为评论长度提供多少空间，这可能是一个 TextField！现在，我们将强制评论简短，不超过 255 个字符。然后，我们还将链接到 author 字段，以便用评论自动填充当前用户。

对于所有多对一关系（如 ForeignKey），我们还必须指定 on_delete 选项。我们还明确设置 related_name，以便将来在查询中更容易"向后"跟踪外键关系。请注意，此名称必须是唯一的，以避免将来出现问题。最后使用 get_user_model 来引用我们的自定义用户模型。

为我们的更改创建一个新的迁移文件，然后运行 migrate 来应用它们。

```shell
$ docker-compose exec web python manage.py makemigrations books
Migrations for 'books':
  books/migrations/0002_review.py - Create model Review
$ docker-compose exec web python manage.py migrate
Operations to perform:
  Apply all migrations: account, accounts, admin, auth, books, contenttypes, sessions, si\
tes
Running migrations:
  Applying books.0002_review... OK
```

## Admin

要使评论应用出现在管理界面中，我们需要通过添加 Review 模型并指定 TabularInline 的显示来大幅更新 books/admin.py。

```python
# books/admin.py

from django.contrib import admin
from .models import Book, Review

class ReviewInline(admin.TabularInline):
    model = Review

class BookAdmin(admin.ModelAdmin):
    inlines = [
        ReviewInline,
    ]
    list_display = ("title", "author", "price",)

admin.site.register(Book, BookAdmin)
```

现在导航到 http://127.0.0.1:8000/admin/books/book/ 的 books 部分，然后点击任何一本书，查看个别书籍页面上可见的评论。

此时，我们仅限于现有用户的评论，尽管我们之前创建了一个testuser@email.com，但在上一章中删除数据库卷挂载时已将其删除。添加此帐户有两种选择：我们可以转到主站点并使用"Sign Up"链接，或者可以直接从管理界面添加它。让我们选择后者。

从管理主页的 Users 部分点击"+ Add"按钮。添加一个名为 testuser 的新用户和密码。点击"Save"按钮。

然后在下一页上添加 testuser@email.com 作为电子邮件地址。您是否注意到用户的密码现在已加密？Django 不存储原始密码，这意味着即使作为超级用户，我们也无法查看个别用户密码。我们可以将密码更改为其他内容，但不能只是复制和粘贴用户密码。

滚动到页面底部，点击"Save"按钮。

好的，最后，我们可以使用 testuser 向"Django for Professionals"书籍添加评论。导航回 Books 部分并点击正确的书籍。写两条评论，并确保将 AUTHOR 选择为 testuser。

## 模板

设置好评论模型后，是时候更新我们的模板，以在每本书的个别页面上显示评论了。添加一个基本的"Reviews"部分，然后循环显示所有现有评论。由于这是一个外键关系，我们通过使用 book.reviews.all 来跟踪它。然后用 review.review 显示评论字段，用 review.author 显示作者。

```html
<!-- templates/books/book_detail.html  -->
{% extends "_base.html" %} {% block title %}{{ book.title }}{% endblock title %}
{% block content %}

<div class="book-detail">
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

就是这样！导航到"Django for Professionals"个别页面查看结果。由于我们使用的是 UUID，您的 URL 将与此处的不同。

## 测试

是时候进行测试了。我们需要为我们的评论创建一个新用户，并在测试套件的 setUpTestData 方法中添加一条评论。然后我们可以测试书籍对象是否包含正确的评论。

这涉及导入 get_user_model 以及在顶部添加 Review 模型。我们可以使用 create_user 创建一个名为 reviewuser 的新用户，然后创建一个链接到我们单一书籍对象的评论对象。最后，在 test_book_detail_view 下，我们可以向响应对象添加一个额外的 assertContains 测试。

```python
# books/tests.py

from django.contrib.auth import get_user_model # new
from django.test import TestCase
from django.urls import reverse

from .models import Book, Review # new

class BookTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(  # new
            username="reviewuser",
            email="reviewuser@email.com",
            password="testpass123",
        )

        cls.book = Book.objects.create(
            title="Harry Potter",
            author="JK Rowling",
            price="25.00",
        )

        cls.review = Review.objects.create(  # new
            book=cls.book,
            author=cls.user,
            review="An excellent review",
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
        self.assertContains(response, "An excellent review")  # new
        self.assertTemplateUsed(response, "books/book_detail.html")
```

如果现在运行测试，它们都应该通过。

```shell
$ docker-compose exec web python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................

---

Ran 17 tests in 0.260s

OK
Destroying test database for alias 'default'...
```

## Git

将我们的新代码更改添加到 Git 中，并包含本章的提交消息。

```shell
$ git status
$ git add .
$ git commit -m 'ch12'
```

本章的代码可以在官方 Github 存储库中找到。

## 结论

如果有更多时间，我们可能会使用页面上的表单来更新评论功能，但这意味着使用 htmx、jQuery、React、Vue 或其他专用 JavaScript 框架进行 AJAX 调用。不幸的是，完全涵盖这一点远远超出了本书的范围。

随着项目的增长，将评论分离成自己的专用应用可能也有意义。这样做是一个非常主观的决定。一般来说，尽可能保持简单——在现有应用中添加外键，直到它变得太大而难以理解——是一种可靠的方法。

在下一章中，我们将向我们的网站添加图片上传功能，以便每本书都可以有封面。
