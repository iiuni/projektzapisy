# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('receive_mass_mail_enrollment', models.BooleanField(default=True, verbose_name=b'otrzymuje mailem og\xc5\x82oszenia Zapis\xc3\xb3w')),
                ('receive_mass_mail_offer', models.BooleanField(default=True, verbose_name=b'otrzymuje mailem og\xc5\x82oszenia OD')),
                ('receive_mass_mail_grade', models.BooleanField(default=True, verbose_name=b'otrzymuje mailem og\xc5\x82oszenia Oceny Zaj\xc4\x99\xc4\x87')),
                ('last_news_view', models.DateTimeField(default=datetime.datetime(2017, 5, 29, 16, 17, 10, 129201))),
                ('consultations', models.TextField(null=True, verbose_name=b'konsultacje', blank=True)),
                ('homepage', models.URLField(default=b'', null=True, verbose_name=b'strona domowa', blank=True)),
                ('room', models.CharField(max_length=20, null=True, verbose_name=b'pok\xc3\xb3j', blank=True)),
                ('status', models.PositiveIntegerField(default=0, verbose_name=b'Status', choices=[(0, b'aktywny'), (1, b'nieaktywny')])),
                ('title', models.CharField(max_length=20, null=True, verbose_name=b'tytu\xc5\x82 naukowy', blank=True)),
            ],
            options={
                'ordering': ['user__last_name', 'user__first_name'],
                'verbose_name': 'pracownik',
                'verbose_name_plural': 'Pracownicy',
                'permissions': (('mailto_all_students', 'Mo\\u017ce wysy\\u0142a\\u0107 maile do wszystkich student\xf3w'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('is_student', models.BooleanField(default=False, verbose_name=b'czy student?')),
                ('is_employee', models.BooleanField(default=False, verbose_name=b'czy pracownik?')),
                ('is_zamawiany', models.BooleanField(default=False, verbose_name=b'czy zamawiany?')),
            ],
            options={
                'verbose_name': 'u\\u017cutkownik',
                'verbose_name_plural': 'u\\u017cytkownicy',
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name=b'Program')),
            ],
            options={
                'verbose_name': 'Program studi\xf3w',
                'verbose_name_plural': 'Programy studi\xf3w',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('receive_mass_mail_enrollment', models.BooleanField(default=True, verbose_name=b'otrzymuje mailem og\xc5\x82oszenia Zapis\xc3\xb3w')),
                ('receive_mass_mail_offer', models.BooleanField(default=True, verbose_name=b'otrzymuje mailem og\xc5\x82oszenia OD')),
                ('receive_mass_mail_grade', models.BooleanField(default=True, verbose_name=b'otrzymuje mailem og\xc5\x82oszenia Oceny Zaj\xc4\x99\xc4\x87')),
                ('last_news_view', models.DateTimeField(default=datetime.datetime(2017, 5, 29, 16, 17, 10, 129201))),
                ('matricula', models.CharField(default=b'', unique=True, max_length=20, verbose_name=b'Numer indeksu')),
                ('ects', models.PositiveIntegerField(default=0, verbose_name=b'punkty ECTS')),
                ('records_opening_bonus_minutes', models.PositiveIntegerField(default=0, verbose_name=b'Przyspieszenie otwarcia zapis\xc3\xb3w (minuty)')),
                ('block', models.BooleanField(default=False, verbose_name=b'blokada planu')),
                ('semestr', models.PositiveIntegerField(default=0, verbose_name=b'Semestr')),
                ('status', models.PositiveIntegerField(default=0, help_text=b'0 - aktywny student, 1 - skre\xc5\x9blony student', verbose_name=b'Status')),
                ('t0', models.DateTimeField(null=True, blank=True)),
                ('isim', models.BooleanField(default=False)),
                ('ects_in_semester', models.SmallIntegerField(default=0)),
                ('dyskretna_l', models.BooleanField(default=False)),
                ('numeryczna_l', models.BooleanField(default=False)),
                ('algorytmy_l', models.BooleanField(default=False)),
                ('programowanie_l', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['user__last_name', 'user__first_name'],
                'verbose_name': 'student',
                'verbose_name_plural': 'studenci',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpeningTimesView',
            fields=[
                ('student', models.ForeignKey(related_name='opening_times', primary_key=True, serialize=False, to='users.Student', on_delete=models.CASCADE)),
                ('opening_time', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudiaZamawiane',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points', models.FloatField(null=True, verbose_name=b'Punkty', blank=True)),
                ('comments', models.TextField(null=True, verbose_name=b'Uwagi', blank=True)),
                ('bank_account', models.CharField(max_length=40, null=True, verbose_name=b'Numer konta bankowego', blank=True)),
                ('student', models.OneToOneField(related_name='zamawiane', verbose_name=b'Student', to='users.Student', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Studia zamawiane2009',
                'verbose_name_plural': 'Studia zamawiane2009',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudiaZamawiane2012',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points', models.FloatField(null=True, verbose_name=b'Punkty', blank=True)),
                ('comments', models.TextField(null=True, verbose_name=b'Uwagi', blank=True)),
                ('bank_account', models.CharField(max_length=40, null=True, verbose_name=b'Numer konta bankowego', blank=True)),
                ('student', models.OneToOneField(related_name='zamawiane2012', verbose_name=b'Student', to='users.Student', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Studia zamawiane2012',
                'verbose_name_plural': 'Studia zamawiane2012',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudiaZamawianeMaileOpiekunow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Studia zamawiane - opiekunowie',
                'verbose_name_plural': 'Studia zamawiane - opiekunowie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_student', models.BooleanField(default=False, verbose_name=b'czy student?')),
                ('is_employee', models.BooleanField(default=False, verbose_name=b'czy pracownik?')),
                ('is_zamawiany', models.BooleanField(default=False, verbose_name=b'czy zamawiany?')),
                ('preferred_language', models.CharField(default=b'pl', max_length=5, verbose_name=b'preferowany j\xc4\x99zyk Systemu Zapis\xc3\xb3w', choices=[(b'pl', b'Polish'), (b'en', b'English')])),
                ('user', models.OneToOneField(related_name='_profile_cache', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='student',
            name='program',
            field=models.ForeignKey(default=None, verbose_name=b'Program Studi\xc3\xb3w', to='users.Program', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(related_name='student', verbose_name=b'U\xc5\xbcytkownik', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
