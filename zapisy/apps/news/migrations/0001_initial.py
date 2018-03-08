

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Tytu\u0142')),
                ('body', models.TextField(verbose_name='Tre\u015b\u0107', blank=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('category', models.CharField(default=b'-', max_length=15, verbose_name='Kategoria', choices=[(b'-', b'Hidden'), (b'offer', b'Oferta'), (b'enrollment', b'Zapisy'), (b'grade', b'Ocena zaj\xc4\x99\xc4\x87')])),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-date', '-id'],
                'get_latest_by': 'date',
                'verbose_name': 'Og\u0142oszenie',
                'verbose_name_plural': 'Og\u0142oszenia',
            },
            bases=(models.Model,),
        ),
    ]
