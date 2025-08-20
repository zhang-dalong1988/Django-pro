from django.views.generic import ListView, DetailView  # 新增

from .models import Book


class BookListView(ListView):
    model = Book
    context_object_name = "book_list"  # 新增
    template_name = "books/book_list.html"


class BookDetailView(DetailView):  # 新增
    model = Book
    context_object_name = "book"  # 新增
    template_name = "books/book_detail.html"
