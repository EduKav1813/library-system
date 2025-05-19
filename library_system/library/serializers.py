from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["full_name"]

    permission_classes = [IsAuthenticated]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["isbn", "title", "authors"]

    permission_classes = [IsAuthenticated]
