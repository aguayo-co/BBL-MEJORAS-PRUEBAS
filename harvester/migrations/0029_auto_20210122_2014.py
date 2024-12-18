# Generated by Django 2.2.10 on 2021-01-22 20:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvester', '0028_auto_20210121_0153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(max_length=3000, validators=[django.core.validators.MinLengthValidator(100, message='Asegúrate de que este valor tenga como mínimo %(limit_value)s (este tiene %(show_value)s).')], verbose_name='reseña'),
        ),
    ]
