# Generated by Django 2.2.10 on 2021-10-21 03:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvester', '0038_auto_20210623_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='relevance',
            field=models.IntegerField(default=1, help_text='La relevancia de la fuente afecta el orden de los Recursos en algunos listados. Números menores aparecen de primero en los listados.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='relevancia'),
        ),
    ]
