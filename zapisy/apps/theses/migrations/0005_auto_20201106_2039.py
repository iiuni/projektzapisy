# Generated by Django 3.1.3 on 2020-11-06 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theses', '0004_migrate_votes_and_remarks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thesis',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
