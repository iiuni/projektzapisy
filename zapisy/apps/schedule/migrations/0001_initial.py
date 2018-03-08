

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True, verbose_name='Tytu\u0142', blank=True)),
                ('description', models.TextField(verbose_name='Opis', blank=True)),
                ('type', models.CharField(max_length=1, verbose_name='Typ', choices=[(b'0', 'Egzamin'), (b'1', 'Kolokwium'), (b'2', 'Wydarzenie'), (b'3', 'Zaj\u0119cia'), (b'4', 'Inne')])),
                ('visible', models.BooleanField(verbose_name='Wydarzenie jest publiczne')),
                ('status', models.CharField(default=b'0', max_length=1, verbose_name='Stan', choices=[(b'0', 'Do rozpatrzenia'), (b'1', 'Zaakceptowane'), (b'2', 'Odrzucone')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-created',),
                'verbose_name': 'wydarzenie',
                'verbose_name_plural': 'wydarzenia',
                'permissions': (('manage_events', 'Mo\u017ce zarz\u0105dza\u0107 wydarzeniami'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(verbose_name='Wiadomo\u015b\u0107')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'wiadomo\u015b\u0107 wydarzenia',
                'verbose_name_plural': 'wiadomo\u015bci wydarzenia',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventModerationMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(verbose_name='Wiadomo\u015b\u0107')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'wiadomo\u015b\u0107 moderacji wydarzenia',
                'verbose_name_plural': 'wiadomo\u015bci moderacji wydarzenia',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpecialReservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('dayOfWeek', models.CharField(max_length=1, verbose_name=b'dzie\xc5\x84 tygodnia', choices=[(b'1', 'poniedzialek'), (b'2', 'wtorek'), (b'3', 'sroda'), (b'4', 'czwartek'), (b'5', 'piatek'), (b'6', 'sobota'), (b'7', 'niedziela')])),
                ('start_time', models.TimeField(verbose_name=b'rozpocz\xc4\x99cie')),
                ('end_time', models.TimeField(verbose_name=b'zako\xc5\x84czenie')),
            ],
            options={
                'verbose_name': 'rezerwacja sta\u0142a',
                'verbose_name_plural': 'rezerwacje sta\u0142e',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField(verbose_name='Dzie\u0144')),
                ('start', models.TimeField(verbose_name='Pocz\u0105tek')),
                ('end', models.TimeField(verbose_name='Koniec')),
                ('place', models.CharField(max_length=255, null=True, verbose_name='Miejsce', blank=True)),
                ('event', models.ForeignKey(verbose_name='Wydarzenie', to='schedule.Event', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['day', 'start', 'end'],
                'get_latest_by': 'end',
                'verbose_name': 'termin',
                'verbose_name_plural': 'terminy',
            },
            bases=(models.Model,),
        ),
    ]
