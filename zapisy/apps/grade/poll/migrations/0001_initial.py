

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LastVisit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'ogladane',
                'verbose_name_plural': 'ogladane',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleChoiceQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=250, verbose_name=b'tre\xc5\x9b\xc4\x87')),
                ('description', models.TextField(null=True, verbose_name=b'opis', blank=True)),
                ('has_other', models.BooleanField(verbose_name=b'opcja inne')),
                ('choice_limit', models.IntegerField(verbose_name=b'maksimum opcji do wyboru')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'pytanie wielokrotnego wyboru',
                'verbose_name_plural': 'pytania wielokrotnego wyboru',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleChoiceQuestionAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('other', models.CharField(max_length=100, null=True, verbose_name=b'inne', blank=True)),
            ],
            options={
                'verbose_name': 'odpowied\\u017a na pytanie wielokrotnego wyboru',
                'verbose_name_plural': 'odpowiedzi na pytania wielokrotnego wyboru',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleChoiceQuestionOrdering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(verbose_name=b'pozycja')),
            ],
            options={
                'ordering': ['sections', 'position'],
                'verbose_name': 'pozycja pyta\\u0144 wielokrotnego wyboru',
                'verbose_name_plural': 'pozycje pyta\\u0144 wielokrotnego wyboru',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=250, verbose_name=b'tre\xc5\x9b\xc4\x87')),
                ('description', models.TextField(null=True, verbose_name=b'opis', blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'pytanie otwarte',
                'verbose_name_plural': 'pytania otwarte',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenQuestionAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('content', models.TextField(null=True, verbose_name=b'tre\xc5\x9b\xc4\x87', blank=True)),
            ],
            options={
                'verbose_name': 'odpowied\\u017a na pytanie otwarte',
                'verbose_name_plural': 'odpowiedzi na pytania otwarte',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OpenQuestionOrdering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(verbose_name=b'pozycja')),
            ],
            options={
                'ordering': ['sections', 'position'],
                'verbose_name': 'pozycja pyta\\u0144 otwartych',
                'verbose_name_plural': 'pozycje pyta\\u0144 otwartych',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=250, verbose_name=b'tre\xc5\x9b\xc4\x87')),
            ],
            options={
                'verbose_name': 'opcja',
                'verbose_name_plural': 'opcje',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Origin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'zestaw ankiet',
                'verbose_name_plural': 'zestawy ankiet',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=40, verbose_name=b'tytu\xc5\x82')),
                ('description', models.TextField(verbose_name=b'opis', blank=True)),
                ('share_result', models.BooleanField(default=False, verbose_name=b'udost\xc4\x99pnij wyniki')),
                ('finished', models.BooleanField(default=False, verbose_name=b'zako\xc5\x84czona')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'usuni\xc4\x99ta')),
            ],
            options={
                'verbose_name': 'ankieta',
                'verbose_name_plural': 'ankiety',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SavedTicket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticket', models.TextField(verbose_name=b'bilet')),
                ('finished', models.BooleanField(verbose_name=b'czy zako\xc5\x84czona')),
            ],
            options={
                'verbose_name': 'zapisany bilet',
                'verbose_name_plural': 'zapisane bilety',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name=b'tytu\xc5\x82')),
                ('description', models.TextField(verbose_name=b'opis', blank=True)),
                ('deleted', models.BooleanField(default=False, verbose_name=b'usuni\xc4\x99ta')),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'sekcja',
                'verbose_name_plural': 'sekcje',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionOrdering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(verbose_name=b'pozycja')),
            ],
            options={
                'ordering': ['poll', 'position'],
                'verbose_name': 'pozycja sekcji',
                'verbose_name_plural': 'pozycje sekcji',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SingleChoiceQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=250, verbose_name=b'tre\xc5\x9b\xc4\x87')),
                ('description', models.TextField(null=True, verbose_name=b'opis', blank=True)),
                ('is_scale', models.BooleanField(verbose_name=b'skala')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'pytanie jednokrotnego wyboru',
                'verbose_name_plural': 'pytania jednokrotnego wyboru',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SingleChoiceQuestionAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'odpowied\\u017a na pytanie jednokrotnego wyboru',
                'verbose_name_plural': 'odpowiedzi na pytania jednokrotnego wyboru',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SingleChoiceQuestionOrdering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(verbose_name=b'pozycja')),
                ('is_leading', models.BooleanField(verbose_name=b'pytanie wiod\xc4\x85ce')),
            ],
            options={
                'ordering': ['sections', '-is_leading', 'position'],
                'verbose_name': 'pozycja pyta\\u0144 jednokrotnego wyboru',
                'verbose_name_plural': 'pozycje pyta\\u0144 jednokrotnego wyboru',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=40, verbose_name=b'tytu\xc5\x82')),
                ('description', models.TextField(verbose_name=b'opis', blank=True)),
                ('no_course', models.BooleanField(default=False, verbose_name=b'nie przypisany')),
                ('deleted', models.BooleanField(default=False, verbose_name=b'usuni\xc4\x99ty')),
                ('exam', models.BooleanField(default=True, verbose_name=b'przedmiot z egzaminem')),
                ('group_type', models.CharField(blank=True, max_length=2, null=True, verbose_name=b'typ zaj\xc4\x99\xc4\x87', choices=[(b'1', b'wyk\xc5\x82ad'), (b'2', b'\xc4\x87wiczenia'), (b'3', b'pracownia'), (b'5', b'\xc4\x87wiczenio-pracownia'), (b'6', b'seminarium'), (b'7', b'lektorat'), (b'8', b'WF'), (b'9', b'repetytorium'), (b'10', b'projekt')])),
                ('in_grade', models.BooleanField(default=False, verbose_name='Szablon wykorzystywany w ocenie')),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'szablon',
                'verbose_name_plural': 'szablony',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemplateSections',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('section', models.ForeignKey(verbose_name=b'sekcja', to='poll.Section', on_delete=models.CASCADE)),
                ('template', models.ForeignKey(verbose_name=b'ankieta', to='poll.Template', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'pozycja sekcji',
                'verbose_name_plural': 'pozycje sekcji',
            },
            bases=(models.Model,),
        ),
    ]
