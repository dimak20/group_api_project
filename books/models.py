import os
import uuid

from django.db import models
from django.utils.text import slugify


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        ordering = ["last_name", "first_name"]


class Genre(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]


def book_image_file_path(instance, filename) -> os.path:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/movies/", filename)


class Book(models.Model):
    COVER = [("Hard", "Hard"), ("Soft", "Soft")]

    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, related_name="books")
    genres = models.ManyToManyField(Genre, related_name="books")
    cover = models.CharField(choices=COVER, default="Hard", max_length=4)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    image = models.ImageField(null=True, upload_to=book_image_file_path)

    def __str__(self):
        return {self.title}
