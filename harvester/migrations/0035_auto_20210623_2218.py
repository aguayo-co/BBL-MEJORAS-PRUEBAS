# Generated by Django 2.2.10 on 2021-06-23 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("harvester", "0034_auto_20210506_1804"),
    ]

    operations = [
        migrations.AddField(
            model_name="contentresource",
            name="creator_new",
            field=models.ManyToManyField(
                blank=True,
                related_name="creator_resources",
                through="harvester.CreatorEquivalenceRelation",
                to="harvester.ContentResourceEquivalence",
                verbose_name="autor",
            ),
        )
    ]
