# Generated by Django 2.2.10 on 2020-07-30 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("harvester", "0019_auto_20200422_1511")]

    operations = [
        migrations.AddIndex(
            model_name="collection",
            index=models.Index(fields=["title"], name="harvester_c_title_da9f0a_idx"),
        )
    ]
