from django.db import migrations, models
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20171019_1034'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='extendeduser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
