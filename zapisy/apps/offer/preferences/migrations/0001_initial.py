

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hidden', models.BooleanField(default=False, verbose_name=b'ukryte')),
                ('lecture', models.IntegerField(blank=True, null=True, verbose_name=b'wyk\xc5\x82ad', choices=[(3, b'Ch\xc4\x99tnie'), (2, b'By\xc4\x87 mo\xc5\xbce'), (1, b'Raczej nie'), (0, b'Nie')])),
                ('review_lecture', models.IntegerField(blank=True, null=True, verbose_name=b'repetytorium', choices=[(3, b'Ch\xc4\x99tnie'), (2, b'By\xc4\x87 mo\xc5\xbce'), (1, b'Raczej nie'), (0, b'Nie')])),
                ('tutorial', models.IntegerField(blank=True, null=True, verbose_name=b'\xc4\x87wiczenia', choices=[(3, b'Ch\xc4\x99tnie'), (2, b'By\xc4\x87 mo\xc5\xbce'), (1, b'Raczej nie'), (0, b'Nie')])),
                ('lab', models.IntegerField(blank=True, null=True, verbose_name=b'pracownia', choices=[(3, b'Ch\xc4\x99tnie'), (2, b'By\xc4\x87 mo\xc5\xbce'), (1, b'Raczej nie'), (0, b'Nie')])),
                ('tutorial_lab', models.IntegerField(blank=True, null=True, verbose_name=b'\xc4\x87wiczenio-pracownia', choices=[(3, b'Ch\xc4\x99tnie'), (2, b'By\xc4\x87 mo\xc5\xbce'), (1, b'Raczej nie'), (0, b'Nie')])),
                ('seminar', models.IntegerField(blank=True, null=True, verbose_name=b'seminarium', choices=[(3, b'Ch\xc4\x99tnie'), (2, b'By\xc4\x87 mo\xc5\xbce'), (1, b'Raczej nie'), (0, b'Nie')])),
            ],
            options={
                'verbose_name': 'preferencja',
                'verbose_name_plural': 'preferencje',
            },
            bases=(models.Model,),
        ),
    ]
