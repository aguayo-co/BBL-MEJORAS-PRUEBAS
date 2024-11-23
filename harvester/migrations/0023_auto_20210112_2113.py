# Generated by Django 2.2.10 on 2021-01-13 02:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("harvester", "0022_auto_20210105_1635"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collectionandresource",
            name="resource",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collectionandresource",
                to="harvester.ContentResource",
            ),
        ),
        migrations.AlterField(
            model_name="set",
            name="name",
            field=models.CharField(max_length=255, verbose_name="nombre del set"),
        ),
        migrations.AlterField(
            model_name="setandresource",
            name="resource",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="setandresource",
                to="harvester.ContentResource",
            ),
        ),
    ]
