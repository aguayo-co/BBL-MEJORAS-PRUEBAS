# Generated by Django 2.2.10 on 2022-12-14 21:02

from django.db import migrations, models
import django.db.models.deletion
import expositions.editors
import expositions.fields
import expositions.models.components
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtail.snippets.blocks
import wagtailmodelchooser.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0001_squashed_0021'),
        ('expositions', '0054_merge_20221123_1255'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sidebar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Sidebar',
                'verbose_name_plural': 'Sidebars',
            },
        ),
        migrations.AddField(
            model_name='helpcenterpage',
            name='content',
            field=expositions.fields.HelpCenterStreamField(blank=True, null=True, verbose_name='Contenido'),
        ),
        migrations.AddField(
            model_name='helpcenterpage',
            name='description',
            field=models.TextField(blank=True, max_length=400, null=True, verbose_name='Descripción'),
        ),
        migrations.AddField(
            model_name='questionpage',
            name='content',
            field=expositions.fields.ContentStreamField(blank=True, null=True, verbose_name='Contenido'),
        ),
        migrations.AddField(
            model_name='questionpage',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Descripción'),
        ),
        migrations.AddField(
            model_name='questionpage',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailimages.Image', verbose_name='Imagen'),
        ),
        migrations.AddField(
            model_name='questionpage',
            name='promoted_section',
            field=models.BooleanField(default=False, help_text='Destaca la Pregunta en el home de Tema.', verbose_name='promover en sección'),
        ),
        migrations.AlterField(
            model_name='exposition',
            name='exposition_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='expositions.TypeExposition', verbose_name='Tipo de exposición'),
        ),
        migrations.AlterField(
            model_name='expositionsection',
            name='content',
            field=wagtail.fields.StreamField([('rich_text', wagtail.blocks.StructBlock([('title', wagtail.blocks.TextBlock(max_length=150, required=False, verbose_name='Titulo')), ('intro', wagtail.blocks.TextBlock(max_length=200, required=False, verbose_name='Introducción')), ('show_context_delimiter', wagtail.blocks.BooleanBlock(default=True, help_text='muestra una línea delimitadora antes de este componente.', label='Mostrar delimitador de contexto', null=True, required=False)), ('wysiwyg', expositions.editors.FullEditor())])), ('image_gallery', wagtail.snippets.blocks.SnippetChooserBlock('expositions.ImageGallery', label='Galería de Imágenes')), ('video_gallery', wagtail.snippets.blocks.SnippetChooserBlock('expositions.VideoGallery', label='Galería de Vídeos')), ('map', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Map', label='Mapa')), ('cloud', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Cloud', label='Nube de Términos')), ('timeline', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Timeline', label='Línea de Tiempo')), ('narrative', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Narrative', label='Narrativa')), ('avatar_list', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(label='Título de Sección')), ('type', wagtail.blocks.ChoiceBlock(choices=[('text', 'Sin imágenes'), ('image', 'Con imágenes')], label='Visualización')), ('avatar_list', wagtail.blocks.StreamBlock([('user', wagtail.blocks.StructBlock([('user', wagtailmodelchooser.blocks.ModelChooserBlock(label='Seleccione un usuario del sistema', required=True, target_model='custom_user.user')), ('subtitle', wagtail.blocks.CharBlock(help_text='Recuerda no colocar un subtítulo de más de 50 caracteres', label='Cargo o subtítulo del avatar', max_length=50, required=True)), ('extra_info', wagtail.blocks.CharBlock(help_text='Recuerda no colocar información adicional del avatar de más de 50 caracteres', label='Información adicional del avatar', max_length=50, required=False))])), ('custom_user', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('title', wagtail.blocks.CharBlock(help_text='Recuerda no colocar un subtítulo de más de 50 caracteres', label='Nombre o título del avatar', max_length=50, required=True)), ('subtitle', wagtail.blocks.CharBlock(help_text='Recuerda no colocar un subtítulo de más de 50 caracteres', label='Cargo o subtítulo del avatar', max_length=50, required=True)), ('extra_info', wagtail.blocks.CharBlock(help_text='Recuerda no colocar información adicional del avatar de más de 50 caracteres', label='Información adicional del avatar', max_length=50, required=False)), ('url', wagtail.blocks.URLBlock(help_text='Puedes agregar al avatar un link externo', required=False))]))], help_text='Selecciona el tipo Usuario del Sistema si deseas traer un usuario de la Bibliteca Digital de Bogota, de lo contrario puedes crear un avatar desde cero ', label='Tipos de usuario')), ('info', expositions.editors.LimitedEditor(label='Subsección de información', required=False))])), ('section_list', wagtail.blocks.StructBlock([('show_context_delimiter', wagtail.blocks.BooleanBlock(default=True, help_text='Muestra una línea delimitadora antes de este componente.', label='Mostrar delimitador de contexto', null=True, required=False)), ('title', wagtail.blocks.CharBlock(label='Título de Sección', required=False)), ('intro', wagtail.blocks.RichTextBlock(features=['h2', 'h3', 'blockquote', 'underline', 'bold', 'italic', 'superscript', 'subscript', 'link'], label='Texto introductorio', required=False)), ('image_group_list', wagtail.blocks.ListBlock(expositions.models.components.ImageGroupComponent, label='Grupos de Imágenes')), ('closure', wagtail.blocks.RichTextBlock(features=['h2', 'h3', 'blockquote', 'underline', 'bold', 'italic', 'superscript', 'subscript', 'link'], label='Texto de cierre', required=False))])), ('link_to_content_pages', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('subtitle', wagtail.blocks.CharBlock(required=False)), ('links', wagtail.blocks.ListBlock(wagtail.blocks.PageChooserBlock(help_text='Página de contenido', label='Página', page_type=['expositions.ContentPage']), help_text='Páginas de contenido a las que enlazar', label='Enlaces', max_num=4, min_num=1))]))], verbose_name='Contenido'),
        ),
        migrations.CreateModel(
            name='ThemePageSidebarItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('sidebar', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_themes', to='expositions.Sidebar')),
                ('theme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='expositions.ThemePage', verbose_name='Tema')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionPageSidebarItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='expositions.QuestionPage', verbose_name='Pregunta')),
                ('sidebar', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_question', to='expositions.Sidebar')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='questionpage',
            name='sidebar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='expositions.Sidebar', verbose_name='Sidebar'),
        ),
    ]
