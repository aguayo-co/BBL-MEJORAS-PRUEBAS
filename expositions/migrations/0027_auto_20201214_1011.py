# Generated by Django 2.2.10 on 2020-12-14 15:11

from django.db import migrations
import expositions.editors
import wagtail.fields
import wagtail.snippets.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0026_auto_20200914_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expositionsection',
            name='content',
            field=wagtail.fields.StreamField([('rich_text', wagtail.blocks.StructBlock([('show_context_delimiter', wagtail.blocks.BooleanBlock(default=True, help_text='muestra una línea delimitadora antes de este componente.', label='Mostrar delimitador de contexto', null=True, required=False)), ('wysiwyg', expositions.editors.FullEditor())])), ('image_gallery', wagtail.snippets.blocks.SnippetChooserBlock('expositions.ImageGallery', label='Galería de Imágenes')), ('video_gallery', wagtail.snippets.blocks.SnippetChooserBlock('expositions.VideoGallery', label='Galería de Vídeos')), ('map', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Map', label='Mapa')), ('cloud', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Cloud', label='Nube de Términos')), ('timeline', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Timeline', label='Línea de Tiempo')), ('narrative', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Narrative', label='Narrativa'))], verbose_name='Contenido'),
        ),
    ]
