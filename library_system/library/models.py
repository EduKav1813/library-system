from django.db import models


class Author(models.Model):
    full_name = models.CharField()


class Book(models.Model):
    isbn = models.CharField()
    title = models.CharField()
    authors = models.ManyToManyField(Author, related_name="books")

    def get_authors_display(self):
        """Return comma-separated list of author names"""
        return ", ".join([author.full_name for author in self.authors.all()])
