# Generated by Django 2.2.10 on 2022-10-11 16:20

from django.db import migrations
import expositions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0042_homepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='hero',
            field=expositions.fields.HeroStreamField(blank=True, null=True, verbose_name='Banner Hero'),
        ),
    ]
