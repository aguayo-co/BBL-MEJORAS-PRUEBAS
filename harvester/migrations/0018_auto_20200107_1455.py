# Generated by Django 2.2.9 on 2020-01-07 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvester', '0017_auto_20191230_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='description',
            field=models.TextField(max_length=200, verbose_name='descripción'),
        ),
        migrations.AlterField(
            model_name='historicalcollaborativecollection',
            name='description',
            field=models.TextField(max_length=200, verbose_name='descripción'),
        ),
        migrations.AlterField(
            model_name='historicalcollection',
            name='description',
            field=models.TextField(max_length=200, verbose_name='descripción'),
        ),
    ]
