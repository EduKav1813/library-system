from django.db import models
from library.models.author import Author


class Book(models.Model):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author, related_name="books")
    summary = models.TextField(
        None,
        max_length=1000,
        help_text="Brief description of the book",
        null=True,
        blank=True,
    )
    isbn_10 = models.CharField(
        "ISBN-10", max_length=10, null=True, blank=True, unique=True
    )
    isbn_13 = models.CharField(
        "ISBN-13", max_length=13, null=True, blank=True, unique=True
    )
    language = models.CharField(max_length=20, default="English")
    genre = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title

    def get_authors_display(self):
        """Return comma-separated list of author names"""
        return ", ".join([author.full_name for author in self.authors.all()])

    def get_recent_books(self, n=5) -> "Book":
        if n < 1:
            raise ValueError("Number of recent books should be positive")

        return Book.objects.all().order_by("-id")[:n]
