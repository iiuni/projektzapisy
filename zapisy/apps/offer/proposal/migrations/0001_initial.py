

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LearningMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='metoda kszta\u0142cenia')),
            ],
            options={
                'verbose_name': 'Metoda kszta\u0142cenia',
                'verbose_name_plural': 'Metody kszta\u0142cenia',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='nazwa aktywno\u015bci')),
                ('hours', models.IntegerField(verbose_name='liczba godzin')),
            ],
            options={
                'verbose_name': 'Praca w\u0142asna studenta',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Syllabus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('studies_type', models.CharField(default=b'both', max_length=80, verbose_name='Kierunek studi\xf3w', choices=[(b'isim', b'isim'), (b'inf', b'informatyka'), (b'both', b'informatyka, ISIM')])),
                ('year', models.IntegerField(blank=True, null=True, verbose_name='Rok studi\xf3w', choices=[(1, b'1'), (2, b'2'), (3, b'3'), (4, b'4'), (5, b'5')])),
                ('requirements', models.TextField(default=b'', verbose_name='Wymagania wst\u0119pne w zakresie wiedzy, umiej\u0119tno\u015bci i kompetencji spo\u0142ecznych', blank=True)),
                ('objectives', models.TextField(default=b'', verbose_name='Cele przedmiotu', blank=True)),
                ('effects_txt', models.TextField(default=b'', verbose_name='Zak\u0142adane efekty kszta\u0142cenia', blank=True)),
                ('effects_codes', models.TextField(default=b'', help_text=b'Wype\xc5\x82nia DDD', verbose_name='Symbole kierunkowych efekt\xf3w kszta\u0142cenia', blank=True)),
                ('contents', models.TextField(default=b'', verbose_name='Tre\u015bci programowe', blank=True)),
                ('literature', models.TextField(default=b'', verbose_name='Zalecana literatura (podr\u0119czniki)', blank=True)),
                ('passing_form', models.TextField(default=b'', verbose_name='Forma zaliczenia poszczeg\xf3lnych komponent\xf3w przedmiotu/modu\u0142u, spos\xf3b sprawdzenia osi\u0105gni\u0119cia zamierzonych efekt\xf3w kszta\u0142cenia', blank=True)),
                ('exam_hours', models.IntegerField(null=True, verbose_name=b'egzamin', blank=True)),
                ('tests_hours', models.IntegerField(null=True, verbose_name=b'sprawdziany/kolokwia', blank=True)),
                ('project_presentation_hours', models.IntegerField(null=True, verbose_name=b'prezentacja projektu', blank=True)),
            ],
            options={
                'verbose_name': 'Metoda kszta\u0142cenia',
                'verbose_name_plural': 'Metody kszta\u0142cenia',
            },
            bases=(models.Model,),
        ),
    ]
