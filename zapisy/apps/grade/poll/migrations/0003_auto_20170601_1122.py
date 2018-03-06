

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0002_auto_20170529_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multiplechoicequestion',
            name='has_other',
            field=models.BooleanField(default=False, verbose_name=b'opcja inne'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='savedticket',
            name='finished',
            field=models.BooleanField(default=False, verbose_name=b'czy zako\xc5\x84czona'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='singlechoicequestion',
            name='is_scale',
            field=models.BooleanField(default=False, verbose_name=b'skala'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='singlechoicequestionordering',
            name='is_leading',
            field=models.BooleanField(default=False, verbose_name=b'pytanie wiod\xc4\x85ce'),
            preserve_default=True,
        ),
    ]
