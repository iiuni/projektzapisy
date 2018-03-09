from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('desiderata', '0002_auto_20170529_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desiderata',
            name='day',
            field=models.CharField(max_length=1, verbose_name=b'dzie\xc5\x84 tygodnia', choices=[(b'1', 'poniedzia\u0142ek'), (b'2', 'wtorek'), (b'3', '\u015broda'), (b'4', 'czwartek'), (b'5', 'pi\u0105tek'), (b'6', 'sobota'), (b'7', 'niedziela')]),
        ),
    ]
