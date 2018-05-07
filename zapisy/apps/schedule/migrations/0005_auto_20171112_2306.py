from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_auto_20170606_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialreservation',
            name='dayOfWeek',
            field=models.CharField(max_length=1, verbose_name=b'dzie\xc5\x84 tygodnia', choices=[(b'1', 'poniedzia\u0142ek'), (b'2', 'wtorek'), (b'3', '\u015broda'), (b'4', 'czwartek'), (b'5', 'pi\u0105tek'), (b'6', 'sobota'), (b'7', 'niedziela')]),
        ),
    ]
