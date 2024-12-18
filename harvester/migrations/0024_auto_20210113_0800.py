# Generated by Django 2.2.10 on 2021-01-12 16:39

import django.core.validators
import django.db.models.deletion
import gm2m.fields
from django.conf import settings
from django.db import migrations, models

import resources.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('harvester', '0023_auto_20210112_2113'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionsGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('delete', models.BooleanField(default=False, null=True, verbose_name='Borrado programado')),
                ('title', models.CharField(max_length=100, verbose_name='nombre para el grupo de colecciones')),
                ('collections_count_cached', models.IntegerField(editable=False, null=True, verbose_name='número de colecciones')),
                ('collections_count_expiration', models.DateTimeField(editable=False, null=True)),
                ('collections_count_expired', models.BooleanField(default=True, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'grupo de colecciones',
                'verbose_name_plural': 'grupos de colecciones',
                'ordering': ['-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectionsGroupCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('delete', models.BooleanField(default=False, null=True, verbose_name='Borrado programado')),
                ('object_pk', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CreatorEquivalenceRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.SmallIntegerField()),
            ],
            options={
                'ordering': ['position'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CreatorEquivalence',
            fields=[
            ],
            options={
                'verbose_name': 'Autor',
                'verbose_name_plural': 'Autores',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('harvester.equivalence',),
        ),
        migrations.CreateModel(
            name='SubjectEquivalence',
            fields=[
            ],
            options={
                'verbose_name': 'Tema',
                'verbose_name_plural': 'Temas',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('harvester.equivalence',),
        ),
        migrations.AddField(
            model_name='collection',
            name='default_cover_image',
            field=models.FilePathField(match='\\.(jpg|jpeg|png|svg)$', null=True, path='/srv/app/resources/static/biblored/collections/cover_images', verbose_name='Imagen de portada por defecto'),
        ),
        migrations.AddField(
            model_name='equivalence',
            name='id_bne',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Identificador BNE'),
        ),
        migrations.AddField(
            model_name='equivalence',
            name='id_lcsh',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Identificador LCSH'),
        ),
        migrations.AddField(
            model_name='equivalence',
            name='id_lembp',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Identificador LEMBP'),
        ),
        migrations.AddField(
            model_name='equivalence',
            name='id_unesco',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Identificador UNESCO'),
        ),
        migrations.AddField(
            model_name='equivalence',
            name='wikidata_identifier',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Identificador Wikidata'),
        ),
        migrations.AddField(
            model_name='historicalcollaborativecollection',
            name='default_cover_image',
            field=models.FilePathField(match='\\.(jpg|jpeg|png|svg)$', null=True, path='/srv/app/resources/static/biblored/collections/cover_images', verbose_name='Imagen de portada por defecto'),
        ),
        migrations.AddField(
            model_name='historicalcollection',
            name='default_cover_image',
            field=models.FilePathField(match='\\.(jpg|jpeg|png|svg)$', null=True, path='/srv/app/resources/static/biblored/collections/cover_images', verbose_name='Imagen de portada por defecto'),
        ),
        migrations.AddField(
            model_name='review',
            name='title',
            field=models.CharField(max_length=256, null=True, verbose_name='título'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='image',
            field=models.ImageField(blank=True, max_length=2000, null=True, upload_to='collections/images/', validators=[resources.validators.FileSizeValidator(1000000), django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])], verbose_name='foto de portada'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='public',
            field=models.BooleanField(default=True, help_text='Una colección pública es visible por todos los usuarios del portal. Cuando no es pública, sólo el dueño la puede ver.', verbose_name='Colección pública'),
        ),
        migrations.AlterField(
            model_name='contentresourceequivalence',
            name='field',
            field=models.CharField(choices=[('type', 'tipo de contenido'), ('language', 'idioma'), ('rights', 'derechos'), ('subject', 'tema'), ('creator', 'autor')], max_length=255, verbose_name='campo'),
        ),
        migrations.AlterField(
            model_name='equivalence',
            name='field',
            field=models.CharField(choices=[('type', 'tipo de contenido'), ('language', 'idioma'), ('rights', 'derechos'), ('subject', 'tema'), ('creator', 'autor')], max_length=255, verbose_name='campo'),
        ),
        migrations.AlterField(
            model_name='historicalcollaborativecollection',
            name='image',
            field=models.TextField(blank=True, max_length=2000, null=True, validators=[resources.validators.FileSizeValidator(1000000), django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])], verbose_name='foto de portada'),
        ),
        migrations.AlterField(
            model_name='historicalcollaborativecollection',
            name='public',
            field=models.BooleanField(default=True, help_text='Una colección pública es visible por todos los usuarios del portal. Cuando no es pública, sólo el dueño la puede ver.', verbose_name='Colección pública'),
        ),
        migrations.AlterField(
            model_name='historicalcollection',
            name='image',
            field=models.TextField(blank=True, max_length=2000, null=True, validators=[resources.validators.FileSizeValidator(1000000), django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])], verbose_name='foto de portada'),
        ),
        migrations.AlterField(
            model_name='historicalcollection',
            name='public',
            field=models.BooleanField(default=True, help_text='Una colección pública es visible por todos los usuarios del portal. Cuando no es pública, sólo el dueño la puede ver.', verbose_name='Colección pública'),
        ),
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(max_length=1200, validators=[django.core.validators.MinLengthValidator(100)], verbose_name='reseña'),
        ),
        migrations.AddField(
            model_name='creatorequivalencerelation',
            name='contentresource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvester.ContentResource'),
        ),
        migrations.AddField(
            model_name='creatorequivalencerelation',
            name='contentresourceequivalence',
            field=models.ForeignKey(limit_choices_to={'field': 'creator'}, on_delete=django.db.models.deletion.CASCADE, to='harvester.ContentResourceEquivalence'),
        ),
        migrations.AddField(
            model_name='collectionsgroupcollection',
            name='collections_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvester.CollectionsGroup'),
        ),
        migrations.AddField(
            model_name='collectionsgroupcollection',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_type_set_for_collectionsgroupcollection', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='collectionsgroup',
            name='collections',
            field=gm2m.fields.GM2MField(through='harvester.CollectionsGroupCollection', through_fields=['collections_group', 'content_object', 'content_type', 'object_pk']),
        ),
        migrations.AddField(
            model_name='collectionsgroup',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='creatorequivalencerelation',
            unique_together={('contentresource', 'position')},
        ),
        migrations.AddIndex(
            model_name='collectionsgroupcollection',
            index=models.Index(fields=['updated_at'], name='harvester_c_updated_9ecb99_idx'),
        ),
        migrations.AddIndex(
            model_name='collectionsgroup',
            index=models.Index(fields=['updated_at'], name='harvester_c_updated_8a8b0f_idx'),
        ),
        migrations.AddConstraint(
            model_name='collectionsgroup',
            constraint=models.UniqueConstraint(fields=('title', 'owner'), name='unique title - owner combination'),
        ),
    ]
