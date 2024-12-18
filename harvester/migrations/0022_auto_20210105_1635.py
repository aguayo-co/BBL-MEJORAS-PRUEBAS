# Generated by Django 2.2.10 on 2021-01-05 21:35

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("harvester", "0021_auto_20201214_1011"),
    ]

    operations = [
        migrations.AddField(
            model_name="collection",
            name="resources_by_type_count_cached",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                editable=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="collection",
            name="resources_by_type_count_expiration",
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="collection",
            name="resources_by_type_count_expired",
            field=models.BooleanField(default=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="historicalcollaborativecollection",
            name="resources_by_type_count_cached",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                editable=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="historicalcollaborativecollection",
            name="resources_by_type_count_expiration",
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="historicalcollaborativecollection",
            name="resources_by_type_count_expired",
            field=models.BooleanField(default=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="historicalcollection",
            name="resources_by_type_count_cached",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                editable=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="historicalcollection",
            name="resources_by_type_count_expiration",
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="historicalcollection",
            name="resources_by_type_count_expired",
            field=models.BooleanField(default=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="set",
            name="resources_by_type_count_cached",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                editable=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="set",
            name="resources_by_type_count_expiration",
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="set",
            name="resources_by_type_count_expired",
            field=models.BooleanField(default=True, editable=False, null=True),
        ),
    ]
