# Generated by Django 3.2.13 on 2022-04-15 08:48

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [("core", "0001_initial"), ("core", "0002_auto_20220415_0847")]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("location", models.CharField(max_length=50)),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                ("visible", models.BooleanField(default=False)),
                ("active", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ("start_date", "name"),
            },
        ),
    ]