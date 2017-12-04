# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticket_create', '0001_initial'),
        ('users', '0001_initial'),
        ('poll', '0002_auto_20170529_1617'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usedticketstamp',
            name='student',
            field=models.ForeignKey(verbose_name=b'student', to='users.Student'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentgraded',
            name='semester',
            field=models.ForeignKey(verbose_name=b'semestr', to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentgraded',
            name='student',
            field=models.ForeignKey(verbose_name=b'student', to='users.Student'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publickey',
            name='poll',
            field=models.ForeignKey(verbose_name=b'ankieta', to='poll.Poll'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='privatekey',
            name='poll',
            field=models.ForeignKey(verbose_name=b'ankieta', to='poll.Poll'),
            preserve_default=True,
        ),
    ]
