# Generated by Django 2.1.8 on 2019-08-03 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0025_type_obligatory'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseinformation',
            name='discipline',
            field=models.CharField(default='Informatyka', max_length=100, verbose_name='dyscyplina'),
        ),
    ]
