import requests
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Author, Book
from .serializers import BookSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def index(request):
    """
    Public view for the landing page
    """
    recent_books = Book.objects.all().order_by("-id")[:5]
    serializer = BookSerializer(recent_books, many=True)
    return render(request, "index.html", {"recent_books": serializer.data})


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
def add_book_by_isbn_10(request):
    """Add a book from ISBN-10 alone.

    All the book data will be fetched via the OpenLibrary API.
    """
    isbn_10 = request.data.get("isbn_10", "").strip()

    if not isbn_10:
        return Response(
            {"error": "ISBN-10 is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    if Book.objects.filter(isbn_10=isbn_10).exists():
        return Response(
            {"error": "Book already exists."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch from Open Library API
    api_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn_10}&format=json&jscmd=data"
    response = requests.get(api_url)
    data = response.json()
    book_data = data.get(f"ISBN:{isbn_10}")

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
        isbn_10=isbn_10,
    )
    book.authors.set(Author.objects.filter(full_name__in=authors))
    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_recent_books(request):
    """
    Get n recent books
    """
    try:
        n = int(request.query_params.get("number_of_books", 5))
    except (TypeError, ValueError):
        return Response({"error": "'number_of_books' must be an integer"}, status=400)

    if n > 100:
        return Response({"error": "'number_of_books' cannot exceed 100"}, status=400)

    recent_books = Book.get_recent_books(n)
    serializer = BookSerializer(recent_books, many=True)
    return Response({"recent_books": serializer.data})
