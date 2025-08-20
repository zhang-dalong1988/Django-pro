from django.urls import path

from .views import BookListView, BookDetailView  # 新增


urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("<uuid:pk>", BookDetailView.as_view(), name="book_detail"),  # 新增
]
