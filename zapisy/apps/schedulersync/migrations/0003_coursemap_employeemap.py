# Generated by Django 2.1.15 on 2020-02-01 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20191020_1023'),
        ('proposal', '0008_auto_20190528_1403'),
        ('schedulersync', '0002_auto_20180201_2236'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduler_course', models.CharField(max_length=100, unique=True, verbose_name='nazwa kursu schedulera')),
                ('proposal', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='proposal.Proposal', verbose_name='propozycja przedmiotu')),
            ],
            options={
                'verbose_name': 'Mapa przedmiotów',
                'verbose_name_plural': 'Mapy przedmiotów',
            },
        ),
        migrations.CreateModel(
            name='EmployeeMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduler_username', models.CharField(max_length=150, unique=True, verbose_name='username schedulera')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Employee', verbose_name='pracownik')),
            ],
            options={
                'verbose_name': 'Mapa pracowników',
                'verbose_name_plural': 'Mapy pracowników',
            },
        ),
    ]
