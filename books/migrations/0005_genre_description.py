# Generated by Django 5.1.2 on 2024-10-20 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0004_alter_book_options_book_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="genre",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
