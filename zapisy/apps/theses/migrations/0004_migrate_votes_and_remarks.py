# Generated by Django 2.1.13 on 2020-01-28 01:46

import apps.theses.enums
from django.db import migrations, models
import django.db.models.deletion


def migrate_data(apps, schema_editor):
    Thesisvotebinding = apps.get_model('theses', 'ThesisVoteBinding')
    Vote = apps.get_model('theses', 'Vote')
    Remark = apps.get_model('theses', 'Remark')
    for t in Thesisvotebinding.objects.all():
        Vote.objects.create(owner=t.voter, vote=t.value, thesis=t.thesis)
        Remark.objects.create(author=t.voter, text=t.reason, thesis=t.thesis)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_auto_20200326_1613'),
        ('theses', '0003_create_theses_board_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Remark',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField(blank=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='remark_author', to='users.Employee')),
                ('thesis',
                 models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='thesis_remarks', to='theses.Thesis')),
            ],
            options={
                'verbose_name': 'uwaga',
                'verbose_name_plural': 'uwagi',
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.SmallIntegerField(choices=[(apps.theses.enums.ThesisVote(1), 'brak głosu'), (
                    apps.theses.enums.ThesisVote(2), 'odrzucona'), (apps.theses.enums.ThesisVote(3), 'zaakceptowana')])),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='vote_owner', to='users.Employee')),
                ('thesis', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE,
                                             related_name='thesis_votes', to='theses.Thesis')),
            ],
            options={
                'verbose_name': 'głos',
                'verbose_name_plural': 'głosy',
            },
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name='thesisvotebinding',
            name='thesis',
        ),
        migrations.RemoveField(
            model_name='thesisvotebinding',
            name='voter',
        ),
        migrations.RemoveField(
            model_name='thesis',
            name='rejection_reason',
        ),
        migrations.AlterField(
            model_name='thesis',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='thesis',
            name='status',
            field=models.SmallIntegerField(blank=True, choices=[(apps.theses.enums.ThesisStatus(1), 'weryfikowana przez komisję'), (apps.theses.enums.ThesisStatus(2), 'zwrócona do poprawek'), (
                apps.theses.enums.ThesisStatus(3), 'zaakceptowana'), (apps.theses.enums.ThesisStatus(4), 'w realizacji'), (apps.theses.enums.ThesisStatus(5), 'obroniona')], null=True),
        ),
        migrations.DeleteModel(
            name='ThesisVoteBinding',
        ),
    ]