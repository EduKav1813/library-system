from django.db import models


class Author(models.Model):
    full_name = models.CharField()


class Book(models.Model):
    ibn = models.CharField()
    title = models.CharField()
    authors = models.ManyToManyField(Author, related_name="books")
