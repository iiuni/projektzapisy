from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0010_discharge_notification_preferences'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationpreferencesstudent',
            name='discharge_approved_student',
        ),
        migrations.RemoveField(
            model_name='notificationpreferencesstudent',
            name='discharge_rejected_student',
        ),
        migrations.RemoveField(
            model_name='notificationpreferencesteacher',
            name='discharge_approved_teacher',
        ),
    ]
