# Generated by Django 2.1.8 on 2019-05-12 22:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_courseinformation'),
        ('proposal', '0006_proposal_semester')
    ]

    operations = [
        migrations.RemoveField(
            model_name='courseinformation',
            name='semester',
        ),
    ]
