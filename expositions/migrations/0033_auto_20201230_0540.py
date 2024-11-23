# Generated by Django 2.2.10 on 2020-12-30 05:40

from django.db import migrations
import expositions.editors
import expositions.models.components
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtail.snippets.blocks
import wagtailmodelchooser.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0032_auto_20201218_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expositionsection',
            name='content',
            field=wagtail.fields.StreamField([('rich_text', wagtail.blocks.StructBlock([('show_context_delimiter', wagtail.blocks.BooleanBlock(default=True, help_text='muestra una línea delimitadora antes de este componente.', label='Mostrar delimitador de contexto', null=True, required=False)), ('wysiwyg', expositions.editors.FullEditor())])), ('image_gallery', wagtail.snippets.blocks.SnippetChooserBlock('expositions.ImageGallery', label='Galería de Imágenes')), ('video_gallery', wagtail.snippets.blocks.SnippetChooserBlock('expositions.VideoGallery', label='Galería de Vídeos')), ('map', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Map', label='Mapa')), ('cloud', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Cloud', label='Nube de Términos')), ('timeline', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Timeline', label='Línea de Tiempo')), ('narrative', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Narrative', label='Narrativa')), ('avatar_list', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(label='Título de Sección')), ('type', wagtail.blocks.ChoiceBlock(choices=[('text', 'Sin imágenes'), ('image', 'Con imágenes')], label='Visualización')), ('avatar_list', wagtail.blocks.StreamBlock([('user', wagtail.blocks.StructBlock([('user', wagtailmodelchooser.blocks.ModelChooserBlock(label='Seleccione un usuario del sistema', required=True, target_model='custom_user.user')), ('subtitle', wagtail.blocks.CharBlock(help_text='Recuerda no colocar un subtítulo de más de 50 caracteres', label='Cargo o subtítulo del avatar', max_length=50, required=True)), ('extra_info', wagtail.blocks.CharBlock(help_text='Recuerda no colocar información adicional del avatar de más de 50 caracteres', label='Información adicional del avatar', max_length=50, required=False))])), ('custom_user', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('title', wagtail.blocks.CharBlock(help_text='Recuerda no colocar un subtítulo de más de 50 caracteres', label='Nombre o título del avatar', max_length=50, required=True)), ('subtitle', wagtail.blocks.CharBlock(help_text='Recuerda no colocar un subtítulo de más de 50 caracteres', label='Cargo o subtítulo del avatar', max_length=50, required=True)), ('extra_info', wagtail.blocks.CharBlock(help_text='Recuerda no colocar información adicional del avatar de más de 50 caracteres', label='Información adicional del avatar', max_length=50, required=False)), ('url', wagtail.blocks.URLBlock(help_text='Puedes agregar al avatar un link externo', required=False))]))], help_text='Selecciona el tipo Usuario del Sistema si deseas traer un usuario de la Bibliteca Digital de Bogota, de lo contrario puedes crear un avatar desde cero ', label='Tipos de usuario')), ('info', expositions.editors.LimitedEditor(label='Subsección de información', required=False))])), ('section_list', wagtail
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              .blocks.StructBlock([('show_context_delimiter', wagtail.blocks.BooleanBlock(default=True, help_text='Muestra una línea delimitadora antes de este componente.', label='Mostrar delimitador de contexto', null=True, required=False)), ('title', wagtail.blocks.CharBlock(label='Título de Sección')), ('intro', wagtail.blocks.RichTextBlock(features=['h2', 'h3', 'blockquote', 'underline', 'bold', 'italic', 'superscript', 'subscript', 'link'], label='Texto introductorio')), ('image_group_list', wagtail.blocks.ListBlock(expositions.models.components.ImageGroupComponent, label='Grupos de Imágenes')), ('closure', wagtail.blocks.RichTextBlock(features=['h2', 'h3', 'blockquote', 'underline', 'bold', 'italic', 'superscript', 'subscript', 'link'], label='Texto de cierre'))]))], verbose_name='Contenido'),
        ),
    ]