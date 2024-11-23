# Generated by Django 4.2.13 on 2024-09-24 21:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('harvester', '0045_auto_20240830_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='Harvest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_source_name', models.CharField(verbose_name='Fuente de datos')),
                ('group_id', models.CharField(verbose_name='Identicador de Tarea')),
                ('status', models.SmallIntegerField(choices=[(0, 'Iniciado'), (1, 'En curso'), (2, 'Completado con errores'), (3, 'Completado correctamente')], default=0, verbose_name='Estado')),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha inicio')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='Fecha fin')),
                ('remaining_time', models.CharField(blank=True, null=True, verbose_name='Tiempo restante estimado')),
                ('counter_resource', models.JSONField(default=dict, null=True, verbose_name='Contador de recursos')),
                ('progress_count', models.BigIntegerField(blank=True, default=0, null=True, verbose_name='Recursos indexados')),
            ],
            options={
                'verbose_name': 'Historial de Cosechamiento',
                'verbose_name_plural': 'Historial de Cosechamientos',
            },
        ),
        migrations.CreateModel(
            name='StageHarvest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.SmallIntegerField(choices=[(0, 'Cosechamiento Creado'), (1, 'Cosechamiento Iniciado'), (2, 'Descargando archivo'), (3, 'Archivo descargado'), (4, 'Archivo no descargado'), (5, 'Archivo guardado'), (6, 'Indexado'), (7, 'Indexado en Curso'), (8, 'Finalizado')], default=0, verbose_name='Etapa')),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha inicio')),
                ('end_date', models.DateTimeField(auto_now_add=True, verbose_name='Fecha fin')),
            ],
        ),
        migrations.AddField(
            model_name='stageharvest',
            name='harvest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvester.harvest', verbose_name='Cosechamiento'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='stage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_harvest_stage', to='harvester.stageharvest', verbose_name='Etapa actual'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario'),
        ),
        migrations.AlterUniqueTogether(
            name='stageharvest',
            unique_together={('stage', 'harvest')},
        ),
    ]