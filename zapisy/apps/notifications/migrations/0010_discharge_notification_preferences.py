from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0009_auto_20240705_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationpreferencesstudent',
            name='discharge_approved_student',
            field=models.BooleanField(default=True, verbose_name='Zatwierdzenie wniosku o wypis dyrektorski'),
        ),
        migrations.AddField(
            model_name='notificationpreferencesstudent',
            name='discharge_rejected_student',
            field=models.BooleanField(default=True, verbose_name='Odrzucenie wniosku o wypis dyrektorski'),
        ),
        migrations.AddField(
            model_name='notificationpreferencesteacher',
            name='discharge_approved_teacher',
            field=models.BooleanField(default=True, verbose_name='Wypis dyrektorski studenta z Twojej grupy'),
        ),
    ]
