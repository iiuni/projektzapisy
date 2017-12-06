# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('private_key', models.TextField(verbose_name=b'klucz prywatny')),
            ],
            options={
                'verbose_name': 'klucz prywatny',
                'verbose_name_plural': 'klucze prywatne',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PublicKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('public_key', models.TextField(verbose_name=b'klucz publiczny')),
            ],
            options={
                'verbose_name': 'klucz publiczny',
                'verbose_name_plural': 'klucze publiczne',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentGraded',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'udzial w ocenie',
                'verbose_name_plural': 'udzial w ocenie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UsedTicketStamp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('poll', models.ForeignKey(verbose_name=b'ankieta', to='poll.Poll')),
            ],
            options={
                'verbose_name': 'wykorzystany bilet',
                'verbose_name_plural': 'wykorzystane bilety',
            },
            bases=(models.Model,),
        ),
    ]
