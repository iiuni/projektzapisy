# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0002_auto_20170529_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='syllabus',
            name='learning_methods',
            field=models.ManyToManyField(to='proposal.LearningMethod', verbose_name='Metody kszta\u0142cenia', blank=True),
        ),
    ]
