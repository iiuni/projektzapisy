import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0037_semester_director_discharge_deadline'),
        ('users', '0025_student_discharge_limit'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectorDischarge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(
                    choices=[(0, 'Oczekujący'), (1, 'Zatwierdzony'), (2, 'Odrzucony')],
                    default=0,
                    verbose_name='Status',
                )),
                ('admin_comment', models.TextField(blank=True, verbose_name='Komentarz administratora')),
                ('decided_at', models.DateTimeField(blank=True, null=True, verbose_name='Data decyzji')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Data złożenia')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='director_discharges',
                    to='courses.courseinstance',
                    verbose_name='Przedmiot',
                )),
                ('decided_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='decided_discharges',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Zatwierdził/Odrzucił',
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='director_discharges',
                    to='users.student',
                    verbose_name='Student',
                )),
            ],
            options={
                'verbose_name': 'Wypis dyrektorski',
                'verbose_name_plural': 'Wypisy dyrektorskie',
                'ordering': ['-created'],
                'unique_together': {('student', 'course')},
            },
        ),
    ]
