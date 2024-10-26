import os
import uuid
from datetime import datetime

from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def __str__(self):
        return self.full_name()

    class Meta:
        ordering = ["last_name", "first_name"]


class Genre(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


def book_image_file_path(instance, filename) -> os.path:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/books/", filename)


class Book(models.Model):
    COVER = [("Hard", "Hard"), ("Soft", "Soft")]

    title = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    authors = models.ManyToManyField(Author, related_name="books")
    genres = models.ManyToManyField(Genre, related_name="books")
    cover = models.CharField(choices=COVER, default="Hard", max_length=4)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    image = models.ImageField(
        upload_to=book_image_file_path, null=True, blank=True
    )

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        ordering = ["id", "title", "year"]

    @staticmethod
    def validate_year(year: int):
        current_year = datetime.now().year
        if year and (year < 1000 or year > current_year):
            raise ValidationError(f"Year must be in: 1000 - {current_year}")

    def clean(self):
        Book.validate_year(self.year)

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Book, self).save(
            force_insert, force_update, using, update_fields
        )

