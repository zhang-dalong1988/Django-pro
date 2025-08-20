from django.db import models
from django.urls import reverse  # 新增
import uuid  # 新增
from django.contrib.auth import get_user_model  # new


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # 新增
    title = models.CharField(max_length=200)  # 书名
    author = models.CharField(max_length=200)  # 作者
    price = models.DecimalField(max_digits=6, decimal_places=2)  # 价格

    def __str__(self):
        return self.title

    def get_absolute_url(self):  # 新增
        return reverse("book_detail", args=[str(self.id)])


class Review(models.Model):  # new
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",  # 用于反向查询的关联名称
    )
    review = models.CharField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.review
