# Generated by Django 3.2.9 on 2021-11-29 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("competitions", "0002_auto_20210331_0822"),
    ]

    operations = [
        migrations.AlterField(
            model_name="genre",
            name="category",
            field=models.CharField(
                choices=[
                    ("other", "Other"),
                    ("creative", "Creative"),
                    ("game", "Game"),
                    ("community", "Community"),
                    ("tgtv", "TGTV"),
                    ("some", "SoMe"),
                ],
                default="other",
                max_length=16,
                verbose_name="Category",
            ),
        ),
    ]
