# Generated by Django 2.2.10 on 2022-10-11 16:48

from django.db import migrations
import expositions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0043_homepage_hero'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='content',
            field=expositions.fields.HomeStreamField(blank=True, null=True, verbose_name='Contenido'),
        ),
    ]
