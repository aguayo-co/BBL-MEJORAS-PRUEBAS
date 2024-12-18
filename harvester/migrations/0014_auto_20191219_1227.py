# Generated by Django 2.2.4 on 2019-12-12 23:33
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("harvester", "0013_auto_20191216_1805")]

    operations = [
        migrations.RemoveConstraint(
            model_name="contentresource", name="unique_resource_per_source"
        ),
        migrations.AddField(
            model_name="contentresource",
            name="dynamic_identifier_expired",
            field=models.BooleanField(default=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="contentresource",
            name="dynamic_identifier_cached",
            field=models.TextField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="contentresource",
            name="dynamic_identifier_expiration",
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]
