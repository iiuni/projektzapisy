from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0036_auto_20211022_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='semester',
            name='director_discharge_deadline',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Termin składania wniosków o wypis dyrektorski',
                help_text='Ostatni dzień, w którym student może złożyć wniosek o wypis dyrektorski. '
                          'Domyślnie: 30 listopada (semestr zimowy) / 30 kwietnia (semestr letni).',
            ),
        ),
    ]
