# Generated by Django 2.2.4 on 2019-08-15 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('mega_red', '0001_initial'), ('mega_red', '0002_remove_country_active'), ('mega_red', '0003_auto_20190710_1321')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('name', models.CharField(max_length=40)),
                ('dian_code', models.IntegerField()),
            ],
            options={
                'verbose_name': 'País',
                'verbose_name_plural': 'Países',
                'ordering': ['-updated_at'],
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='country',
            index=models.Index(fields=['updated_at'], name='mega_red_co_updated_581a11_idx'),
        ),
        migrations.AddConstraint(
            model_name='country',
            constraint=models.UniqueConstraint(fields=('name',), name='mega_red_unique_country_name'),
        ),
        migrations.AddConstraint(
            model_name='country',
            constraint=models.UniqueConstraint(fields=('dian_code',), name='mega_red_unique_country_dian_code'),
        ),
    ]
