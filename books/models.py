from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)


class Genre(models.Model):
    name = models.CharField(max_length=50)


class Book(models.Model):
    COVER = [("Hard", "Hard"), ("Soft", "Soft")]

    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, related_name="books")
    genres = models.ManyToManyField(Genre, related_name="books")
    cover = models.CharField(choices=COVER, default="Hard", max_length=4)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(decimal_places=2, max_digits=5, default=0)
