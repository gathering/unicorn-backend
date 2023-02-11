# Generated by Django 3.2.16 on 2022-11-11 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("competitions", "0008_remove_toornament"),
    ]

    operations = [
        migrations.AddField(
            model_name="competition",
            name="scoring_complete",
            field=models.BooleanField(
                default=False,
                help_text="Scoring is completed and the competition is ready for handing out prices",
                verbose_name="Scoring Completed",
            ),
        ),
    ]