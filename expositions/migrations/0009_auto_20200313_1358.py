# Generated by Django 2.2.10 on 2020-03-13 18:58

from django.db import migrations, models
import django.db.models.deletion
import resources.fields
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0008_auto_20200306_1635'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mapmilestone',
            options={'verbose_name': 'Hito de Mapa', 'verbose_name_plural': 'Hitos de Mapa'},
        ),
        migrations.AlterModelOptions(
            name='timelinemilestone',
            options={'verbose_name': 'Hito de Linea de Tiempo', 'verbose_name_plural': 'Hitos de Linea de Tiempo'},
        ),
        migrations.AddField(
            model_name='map',
            name='image_bottom_corner_bound_latitude',
            field=resources.fields.LatitudeField(blank=True, decimal_places=6, max_digits=8, null=True, verbose_name='Latitud de esquina límite inferior derecha de imagen'),
        ),
        migrations.AddField(
            model_name='map',
            name='image_bottom_corner_bound_longitude',
            field=resources.fields.LongitudeField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Longitud de esquina límite inferior derecha de imagen'),
        ),
        migrations.AddField(
            model_name='map',
            name='image_top_corner_bound_latitude',
            field=resources.fields.LatitudeField(blank=True, decimal_places=6, max_digits=8, null=True, verbose_name='Latitud de esquina límite superior izquierda de imagen'),
        ),
        migrations.AddField(
            model_name='map',
            name='image_top_corner_bound_longitude',
            field=resources.fields.LongitudeField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Longitud de esquina límite superior izquierda de imagen'),
        ),
        migrations.AlterField(
            model_name='expositionsection',
            name='image',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailimages.Image'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='resource',
            name='creator',
            field=models.TextField(blank=True, null=True, verbose_name='Autor'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='title',
            field=models.TextField(blank=True, null=True, verbose_name='Título'),
        ),
        migrations.AlterField(
            model_name='timelinemilestone',
            name='is_avatar',
            field=models.BooleanField(blank=True, choices=[(True, 'Es una Persona')], default=False, verbose_name='Es una Persona'),
        ),
        migrations.AlterField(
            model_name='timelinemilestone',
            name='long_description',
            field=wagtail.fields.RichTextField(),
        ),
    ]