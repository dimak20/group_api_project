# Generated by Django 5.1.2 on 2024-10-21 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0005_genre_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="author",
            name="biography",
            field=models.TextField(blank=True, null=True),
        ),
    ]
