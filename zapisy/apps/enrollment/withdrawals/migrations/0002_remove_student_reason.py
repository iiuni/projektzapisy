from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('withdrawals', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='directorwithdrawal',
            name='student_reason',
        ),
    ]
