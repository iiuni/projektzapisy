

from django.db import models, migrations
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20170529_1617'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField(default=0, verbose_name=b'punkty', choices=[(0, b'0'), (1, b'1'), (2, b'2'), (3, b'3')])),
                ('correction', models.IntegerField(default=0, verbose_name=b'korekta', choices=[(0, b'0'), (1, b'1'), (2, b'2'), (3, b'3')])),
                ('free_vote', models.BooleanField(default=False, verbose_name='G\u0142os nie liczy si\u0119 do limitu')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='courses.Course', null=True)),
                ('entity', models.ForeignKey(verbose_name=b'podstawa', to='courses.CourseEntity', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('student', 'entity', '-value'),
                'verbose_name': 'pojedynczy g\u0142os',
                'verbose_name_plural': 'pojedyncze g\u0142osy',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SystemState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(default=2017, verbose_name=b'Rok akademicki')),
                ('max_points', models.IntegerField(default=50, verbose_name=b'Maksimum punkt\xc3\xb3w na przedmioty')),
                ('max_vote', models.IntegerField(default=3, verbose_name=b'Maksymalna warto\xc5\x9b\xc4\x87 g\xc5\x82osu')),
                ('vote_beg', models.DateField(default=datetime.date(2015, 6, 10), verbose_name=b'Pocz\xc4\x85tek g\xc5\x82osowania')),
                ('vote_end', models.DateField(default=datetime.date(2015, 7, 10), verbose_name=b'Koniec g\xc5\x82osowania')),
                ('winter_correction_beg', models.DateField(default=datetime.date(2015, 1, 1), verbose_name=b'Pocz\xc4\x85tek korekty zimowej')),
                ('winter_correction_end', models.DateField(default=datetime.date(2015, 7, 31), verbose_name=b'Koniec korekty zimowej')),
                ('summer_correction_beg', models.DateField(default=datetime.date(2015, 1, 1), verbose_name=b'Pocz\xc4\x85tek korekty letniej')),
                ('summer_correction_end', models.DateField(default=datetime.date(2015, 7, 31), verbose_name=b'Koniec korekty letniej')),
                ('semester_summer', models.ForeignKey(related_name='summer_votes', verbose_name=b'Semestr letni', blank=True, to='courses.Semester', null=True, on_delete=models.CASCADE)),
                ('semester_winter', models.ForeignKey(related_name='winter_votes', verbose_name=b'Semestr zimowy', blank=True, to='courses.Semester', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'ustawienia g\u0142osowania',
                'verbose_name_plural': 'ustawienia g\u0142osowa\u0144',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='singlevote',
            name='state',
            field=models.ForeignKey(verbose_name=b'ustawienia g\xc5\x82osowania', to='vote.SystemState', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlevote',
            name='student',
            field=models.ForeignKey(verbose_name=b'g\xc5\x82osuj\xc4\x85cy', to='users.Student', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='singlevote',
            unique_together=set([('course', 'state', 'student')]),
        ),
    ]
