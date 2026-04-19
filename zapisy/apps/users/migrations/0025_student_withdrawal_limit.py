from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20201029_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='withdrawal_limit',
            field=models.PositiveIntegerField(
                default=2,
                help_text='Łączna liczba wypisów dyrektorskich, z których student może skorzystać.',
                verbose_name='Limit wypisów dyrektorskich',
            ),
        ),
    ]
