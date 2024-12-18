# Generated by Django 2.2.10 on 2020-05-05 16:13

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0017_auto_20200422_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expositionsection',
            name='rich_text_intro',
            field=models.TextField(blank=True, help_text='Introducción corta que se muestra si la sección de contenido inicia con un texto enriquecido.', max_length=200, null=True, verbose_name='Introducción de Texto Enriquecido'),
        ),
        migrations.AlterField(
            model_name='mapmilestone',
            name='long_description',
            field=wagtail.fields.RichTextField(verbose_name='Descripción Larga'),
        ),
        migrations.AlterField(
            model_name='timelinemilestone',
            name='long_description',
            field=wagtail.fields.RichTextField(verbose_name='Descripción Larga'),
        ),
    ]
