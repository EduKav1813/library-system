import requests
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from library.models import Action, Author, Book, UserAction
from library.serializers import BookSerializer
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


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


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def borrow_book(request, book_id):
    """
    Allows an authenticated user to borrow a book.
    Creates a 'BORROW' action in the UserAction model.
    """
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    # Prevent returning books that are not borrowed
    book_ct = ContentType.objects.get_for_model(Book)

    borrow_count = UserAction.objects.filter(
        user=request.user,
        action_type=Action.BORROW,
        content_type=book_ct,
        object_id=book.id,
    ).count()

    return_count = UserAction.objects.filter(
        user=request.user,
        action_type=Action.RETURN,
        content_type=book_ct,
        object_id=book.id,
    ).count()

    if return_count < borrow_count:
        return Response(
            {"error": "You are already borrowing this book."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    UserAction.objects.create(
        user=user,
        action_type=Action.BORROW,
        content_type=ContentType.objects.get_for_model(Book),
        object_id=book.id,
    )

    return Response(
        {"message": f"You have borrowed '{book.title}'."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def return_book(request, book_id):
    """
    Allows an authenticated user to return borrowed book.
    Creates a 'RETURN' action in the UserAction model.
    """
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    # Prevent returning books that are not borrowed
    book_ct = ContentType.objects.get_for_model(Book)

    borrow_count = UserAction.objects.filter(
        user=request.user,
        action_type=Action.BORROW,
        content_type=book_ct,
        object_id=book.id,
    ).count()

    return_count = UserAction.objects.filter(
        user=request.user,
        action_type=Action.RETURN,
        content_type=book_ct,
        object_id=book.id,
    ).count()

    if borrow_count <= return_count:
        return Response(
            {"error": "You are not borrowing this book."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    UserAction.objects.create(
        user=user,
        action_type=Action.RETURN,
        content_type=ContentType.objects.get_for_model(Book),
        object_id=book.id,
    )

    return Response(
        {"message": f"You have returned '{book.title}'."},
        status=status.HTTP_201_CREATED,
    )
