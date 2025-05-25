from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from library.models.author import Author
from library.models.book import Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["full_name"]

    permission_classes = [IsAuthenticated]


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)

    class Meta:
        model = Book
        fields = ["title", "summary", "isbn_10", "authors"]

    permission_classes = [IsAuthenticated]
