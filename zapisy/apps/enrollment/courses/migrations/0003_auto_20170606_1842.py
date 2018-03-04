# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20170601_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursedescription',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='courseentity',
            name='effects',
            field=models.ManyToManyField(to='courses.Effects', verbose_name='Grupa efekt\xf3w kszta\\u0142cenia', blank=True),
        ),
        migrations.AlterField(
            model_name='term',
            name='classrooms',
            field=models.ManyToManyField(related_name='new_classrooms', verbose_name=b'sale', to='courses.Classroom', blank=True),
        ),
    ]
