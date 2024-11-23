# Generated by Django 2.2.10 on 2020-03-27 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harvester', '0018_auto_20200107_1455'),
        ('expositions', '0010_auto_20200325_1632'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exposition',
            name='subject',
        ),
        migrations.AddField(
            model_name='exposition',
            name='subject',
            field=models.ForeignKey(limit_choices_to={'field': 'subject'}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='harvester.Equivalence'),
        ),
    ]
