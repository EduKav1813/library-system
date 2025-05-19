from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, permissions
import requests

from .models import Book, Author
from .serializers import BookSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def index(request):
    """
    Public view for the landing page
    """
    recent_books = Book.objects.all().order_by("-id")[:5]
    serializer = BookSerializer(recent_books, many=True)
    return Response(
        {"message": "Welcome to the Library API", "recent_books": serializer.data}
    )


def index_template(request):
    """
    Render HTML landing page
    """
    recent_books = Book.objects.all().order_by("-id")[:5]
    return render(request, "index.html", {"recent_books": recent_books})


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Account created for {username}! You can now log in."
            )
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def add_book_by_isbn(request):
    """Add a book from ISBN alone.

    All the book data will be fetched via the OpenLibrary API.
    """
    isbn = request.data.get("isbn", "").strip()

    if not isbn:
        return Response(
            {"error": "ISBN is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    if Book.objects.filter(isbn=isbn).exists():
        return Response(
            {"error": "Book already exists."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch from Open Library API
    api_url = (
        f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    )
    response = requests.get(api_url)
    data = response.json()
    book_data = data.get(f"ISBN:{isbn}")

    if not book_data:
        return Response(
            {"error": "No book found for this ISBN."}, status=status.HTTP_404_NOT_FOUND
        )

    title = book_data.get("title", "Untitled")
    authors = [author["name"] for author in book_data.get("authors", [])]

    for author in authors:
        if not Author.objects.filter(full_name=author):
            Author.objects.create(
                full_name=author,
            )

    book = Book.objects.create(
        title=title,
        isbn=isbn,
    )
    book.authors.set(Author.objects.filter(full_name__in=authors))
    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
