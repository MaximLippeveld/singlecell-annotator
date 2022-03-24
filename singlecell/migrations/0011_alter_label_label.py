# Generated by Django 4.0.2 on 2022-03-24 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('singlecell', '0010_alter_label_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='label',
            name='label',
            field=models.IntegerField(choices=[(0, 'Bad segmentation'), (1, '1 lobe'), (2, '2 lobes'), (3, '3 lobes'), (4, '4 lobes'), (5, '5 lobes'), (6, 'Unclear amount of lobes')], verbose_name='Label'),
        ),
    ]
