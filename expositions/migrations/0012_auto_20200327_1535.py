# Generated by Django 2.2.10 on 2020-03-27 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expositions', '0011_auto_20200327_0958'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeline',
            name='date_group_by',
        ),
        migrations.AlterField(
            model_name='timelinemilestone',
            name='category',
            field=models.CharField(choices=[('category_blue', 'Categoría 1 (Azul)'), ('category_magenta', 'Categoría 2 (Magenta)'), ('category_green', 'Categoría 3 (Verde)'), ('category_purple', 'Categoría 4 (Púrpura)'), ('category_yellow', 'Categoría 5 (Amarilla)'), ('category_red', 'Categoría 6 (Rojo)')], max_length=16, verbose_name='Categoría'),
        ),
        migrations.AlterField(
            model_name='timelinemilestone',
            name='is_avatar',
            field=models.BooleanField(blank=True, default=False, verbose_name='Es una Persona'),
        ),
    ]
