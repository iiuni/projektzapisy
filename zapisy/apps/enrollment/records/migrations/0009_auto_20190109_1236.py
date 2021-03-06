# Generated by Django 2.0.8 on 2019-01-09 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_auto_20180804_2031'),
        ('users', '0012_auto_20180804_2031'),
        ('records', '0008_programgrouprestrictions'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='programgrouprestrictions',
            unique_together={('group', 'program')},
        ),
        migrations.AddIndex(
            model_name='programgrouprestrictions',
            index=models.Index(fields=['group', 'program'], name='records_pro_group_i_802ae5_idx'),
        ),
    ]
