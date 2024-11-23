# Generated by Django 2.2.4 on 2019-10-22 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvester', '0006_auto_20191009_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='equivalence',
            name='cite_type',
            field=models.CharField(blank=True, choices=[('standard', 'Estándar'), ('periodical', 'Publicación periódica')], help_text='Especifica el tipo de citación a usar.', max_length=255, null=True, verbose_name='tipo de citación'),
        ),
        migrations.AddField(
            model_name='equivalence',
            name='full_date',
            field=models.BooleanField(blank=True, help_text='Especifica si se debe imprimir la fecha completa para recursos de este tipo. Si no se marca esta casilla se imprime sólo el año.', null=True, verbose_name='fecha completa'),
        ),
    ]