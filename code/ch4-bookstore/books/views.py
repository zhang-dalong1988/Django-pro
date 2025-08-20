from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,  # new
)
from django.views.generic import ListView, DetailView
from django.db.models import Q  # new

from .models import Book


class BookListView(LoginRequiredMixin, ListView):  # new
    model = Book
    context_object_name = "book_list"
    template_name = "books/book_list.html"
    login_url = "account_login"  # new


class BookDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):  # new
    model = Book
    context_object_name = "book"
    template_name = "books/book_detail.html"
    login_url = "account_login"
    permission_required = "books.special_status"  # new
    # 使用 prefetch_related 优化查询性能
    # 1. Book.objects.all() 获取所有图书记录
    # 2. prefetch_related("reviews__author") 预加载关联的评论及其作者信息
    # - reviews: 通过反向关联获取每本书的所有评论
    # - reviews__author: 进一步获取每条评论的作者信息
    # 这样可以避免 N+1 查询问题,减少数据库查询次数
    queryset = Book.objects.all().prefetch_related(
        "reviews__author",
    )  # new


class SearchResultsListView(ListView):
    model = Book
    context_object_name = "book_list"
    template_name = "books/book_list.html"

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        return Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
