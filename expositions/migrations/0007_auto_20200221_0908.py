# Generated by Django 2.2.10 on 2020-02-21 14:08

from django.db import migrations, models
import django.db.models.deletion
import expositions.edit_handlers
import expositions.editors
import modelcluster.fields
import wagtail.fields
import wagtail.snippets.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('harvester', '0018_auto_20200107_1455'),
        ('expositions', '0006_auto_20200207_2135'),
    ]

    operations = [
        migrations.CreateModel(
            name='Narrative',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='Título')),
                ('description', models.TextField(verbose_name='Descripción')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='exposition',
            name='content',
        ),
        migrations.AddField(
            model_name='expositionsection',
            name='long_description',
            field=models.TextField(default=None, verbose_name='Descripción Larga'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expositionsection',
            name='short_description',
            field=models.TextField(default=None, max_length=200, verbose_name='Descripción Corta'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expositionsection',
            name='subject',
            field=modelcluster.fields.ParentalManyToManyField(limit_choices_to={'field': 'subject'}, to='harvester.Equivalence'),
        ),
        migrations.AddField(
            model_name='imagegallery',
            name='description',
            field=models.TextField(blank=True, verbose_name='Descripción'),
        ),
        migrations.AddField(
            model_name='videogallery',
            name='description',
            field=models.TextField(blank=True, verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='expositionsection',
            name='content',
            field=wagtail.fields.StreamField([('wysiwyg', expositions.editors.FullEditor()), ('image_gallery', wagtail.snippets.blocks.SnippetChooserBlock('expositions.ImageGallery')), ('video_gallery', wagtail.snippets.blocks.SnippetChooserBlock('expositions.VideoGallery')), ('map', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Map')), ('cloud', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Cloud')), ('timeline', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Timeline')), ('narrative', wagtail.snippets.blocks.SnippetChooserBlock('expositions.Narrative'))]),
        ),
        migrations.AlterField(
            model_name='videogallery',
            name='videos',
            field=wagtail.fields.StreamField([('video', expositions.edit_handlers.VideoBlock(label='video'))]),
        ),
        migrations.CreateModel(
            name='NarrativeResource',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='expositions.Resource')),
                ('related_text', wagtail.fields.StreamField([('related_text', expositions.editors.MiniEditor())], verbose_name='Texto Relacionado')),
                ('resource_narrative', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='expositions.Narrative')),
            ],
            options={
                'abstract': False,
            },
            bases=('expositions.resource',),
        ),
    ]