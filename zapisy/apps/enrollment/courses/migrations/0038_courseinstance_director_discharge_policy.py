from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0037_semester_director_discharge_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseinstance',
            name='director_discharge_policy',
            field=models.IntegerField(
                choices=[(0, 'Automatyczny'), (1, 'Zabroniony'), (2, 'Ręczny')],
                default=0,
                verbose_name='Polityka wypisów dyrektorskich',
            ),
        ),
    ]
