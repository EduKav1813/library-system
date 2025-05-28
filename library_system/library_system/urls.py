"""
URL configuration for library_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from library.views import auth, authorized, book_actions, public
from library.viewsets import AuthorViewSet, BookViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"books", BookViewSet)
router.register(r"authors", AuthorViewSet)

urlpatterns = [
    path("", public.index, name="index"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", auth.register_view, name="register"),
    path(
        "api/add-by-isbn-10/",
        book_actions.add_book_by_isbn_10,
        name="add-book-by-isbn-10",
    ),
    path("api/get-recent/", public.get_recent_books, name="get-recent-books"),
    path(
        "api/activity/recent/", public.get_recent_activity, name="get-recent-activity"
    ),
    path("books/", public.books, name="books"),
    path("borrowed-books/", authorized.borrowed_books_view, name="borrowed_books"),
    path(
        "api/borrowed-books/", authorized.borrowed_books_api, name="user_borrowed_books"
    ),
    path(
        "api/book/borrow/<int:book_id>/", book_actions.borrow_book, name="borrow_book"
    ),
    path(
        "api/book/return/<int:book_id>/", book_actions.return_book, name="return_book"
    ),
]
