# Generated by Django 2.2.4 on 2019-08-28 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('harvester', '0002_auto_20190827_1746'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contentresource',
            options={'ordering': ['-updated_at'], 'permissions': (('delete_in_background', 'Borrado en segundo plano'),), 'verbose_name': 'recurso de contenido', 'verbose_name_plural': 'recursos de contenido'},
        ),
    ]
