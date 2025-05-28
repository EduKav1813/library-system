from django.shortcuts import render
from library.serializers import BookSerializer
from library.services.book_service import get_borrowed_books_by_user
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def borrowed_books(request):
    """
    View for all books currently borrowed by the user
    """
    user = request.user
    borrowed_books = get_borrowed_books_by_user(user.id)
    serializer = BookSerializer(borrowed_books, many=True, context={"request": request})
    return render(request, "borrowed_books.html", {"books": serializer.data})
