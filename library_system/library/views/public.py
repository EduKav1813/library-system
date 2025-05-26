from django.shortcuts import render
from library.models import Book, UserAction
from library.serializers import BookSerializer, UserActionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def index(request):
    """
    Public view for the landing page
    """
    recent_books = Book.objects.all().order_by("-id")[:5]
    serializer = BookSerializer(recent_books, many=True)
    return render(request, "index.html", {"recent_books": serializer.data})


@api_view(["GET"])
@permission_classes([AllowAny])
def books(request):
    """
    Public view for the landing page
    """
    recent_books = Book.objects.all().order_by("-id")
    serializer = BookSerializer(recent_books, many=True)
    return render(request, "books.html", {"books": serializer.data})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_recent_books(request):
    """
    Get up to n latest books. Default: 5.
    """
    try:
        n = int(request.query_params.get("number_of_books", 5))
    except (TypeError, ValueError):
        return Response({"error": "'number_of_books' must be an integer"}, status=400)

    recent_books = Book.get_recent(n)
    serializer = BookSerializer(recent_books, many=True)
    return Response({"recent_books": serializer.data})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_recent_activity(request):
    """
    Get up to n entries for recent activity. Default: 5.
    """
    try:
        n = int(request.query_params.get("number_of_actions", 5))
    except (TypeError, ValueError):
        return Response({"error": "'number_of_actions' must be an integer"}, status=400)

    recent_activity = UserAction.get_recent(n)
    serializer = UserActionSerializer(recent_activity, many=True)
    return Response({"recent_activity": serializer.data})
