# Generated by Django 2.2.10 on 2021-10-29 23:32

from django.db import migrations
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0036_auto_20210623_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='milestones_content',
            field=wagtail.fields.StreamField([('map_milestone', wagtail.blocks.StreamBlock([('title', wagtail.blocks.CharBlock(label='Título', max_length=60)), ('short_description', wagtail.blocks.TextBlock(label='Descripción Corta', max_length=300)), ('long_description', wagtail.blocks.RichTextBlock(features=['h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'hr', 'link', 'superscript', 'subscript', 'blockquote'], label='Descripción Larga')), ('publish_date', wagtail.blocks.DateBlock(label='Fecha de Publicación', required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(label='Imagen', required=False)), ('latitude', wagtail.blocks.DecimalBlock(decimal_places=6, label='Latitud', max_digits=8, max_value=90, min_value=-90)), ('longitude', wagtail.blocks.DecimalBlock(decimal_places=6, label='Longitud', max_digits=9, max_value=180, min_value=-180)), ('place', wagtail.blocks.TextBlock(label='Lugar')), ('pin_image', wagtail.images.blocks.ImageChooserBlock(label='Icono del Pin', required=False))]))], default=list, verbose_name='Hitos de Mapa'),
        ),
    ]
