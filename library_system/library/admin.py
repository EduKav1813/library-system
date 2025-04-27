from django.contrib import admin

from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ["full_name"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "display_authors",
        "ibn",
    )
    search_fields = ["title", "authors__name", "ibn"]
    filter_horizontal = (
        "authors",
    )  # This creates a nice interface for selecting multiple authors

    def display_authors(self, obj):
        """Create a string for the authors to display in Admin."""
        return obj.get_authors_display()
