# Generated by Django 3.0.6 on 2020-05-13 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('singlecell', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='label',
            field=models.IntegerField(choices=[(0, 'Discard'), (1, '1-lobe'), (2, '2-lobed'), (3, '3-lobed'), (4, '4-lobed'), (5, 'Unclear')], verbose_name='Label assigned in this annotation'),
        ),
    ]
