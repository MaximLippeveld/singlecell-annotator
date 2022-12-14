# Generated by Django 4.0.2 on 2022-02-23 12:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('singlecell', '0007_alter_annotation_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='indices',
            field=models.CharField(default='', max_length=255, validators=[django.core.validators.int_list_validator], verbose_name='Comma-separated list of channel indices'),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='label',
            field=models.IntegerField(choices=[(-1, 'Not set'), (0, 'Bad segmentation'), (1, '1 lobe'), (2, '2 lobes'), (3, '3 lobes'), (4, '4 lobes'), (5, 'Unclear amount of lobes')], default=-1, verbose_name='Label'),
        ),
    ]
