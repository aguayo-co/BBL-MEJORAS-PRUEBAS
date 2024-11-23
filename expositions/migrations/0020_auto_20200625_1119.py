# Generated by Django 2.2.10 on 2020-06-25 16:19

from django.db import migrations, models
import django.db.models.deletion
import resources.fields


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0019_auto_20200505_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryimage',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.Image', verbose_name='imagen'),
        ),
        migrations.AlterField(
            model_name='imagegallery',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='mapmilestone',
            name='latitude',
            field=resources.fields.LatitudeField(decimal_places=6, max_digits=8, verbose_name='Latitud'),
        ),
        migrations.AlterField(
            model_name='mapmilestone',
            name='longitude',
            field=resources.fields.LongitudeField(decimal_places=6, max_digits=9, verbose_name='Longitud'),
        ),
        migrations.AlterField(
            model_name='videogallery',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Nombre'),
        ),
    ]