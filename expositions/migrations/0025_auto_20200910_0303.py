# Generated by Django 2.2.10 on 2020-09-10 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0024_auto_20200910_0258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expositionsection',
            name='show_context_delimiter',
            field=models.BooleanField(default=True, null=True, verbose_name='Mostrar delimitador de Contexto'),
        ),
    ]