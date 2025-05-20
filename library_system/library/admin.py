from django.contrib import admin

from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = [
        "full_name",
        "first_name",
        "middle_name",
        "last_name",
        "date_of_birth",
        "date_of_death",
    ]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "summary",
        "display_authors",
        "isbn_10",
        "isbn_13",
    )
    search_fields = ["title", "summary", "authors__name", "isbn_10"]
    filter_horizontal = (
        "authors",
    )  # This creates a nice interface for selecting multiple authors

    def display_authors(self, obj):
        """Create a string for the authors to display in Admin."""
        return obj.get_authors_display()
