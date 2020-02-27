from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='author',
            field=models.ForeignKey(verbose_name=b'autor', to='users.Employee', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='template',
            name='course',
            field=models.ForeignKey(verbose_name=b'przedmiot', blank=True, to='courses.CourseEntity', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='template',
            name='sections',
            field=models.ManyToManyField(to='poll.Section', verbose_name=b'sekcje', through='poll.TemplateSections'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='template',
            name='studies_type',
            field=models.ForeignKey(verbose_name=b'typ studi\xc3\xb3w', blank=True, to='users.Program', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlechoicequestionordering',
            name='hide_on',
            field=models.ManyToManyField(to='poll.Option', verbose_name=b'ukryj sekcj\xc4\x99 przy                                                          odpowiedziach', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlechoicequestionordering',
            name='question',
            field=models.ForeignKey(verbose_name=b'pytanie', to='poll.SingleChoiceQuestion', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlechoicequestionordering',
            name='sections',
            field=models.ForeignKey(verbose_name=b'sekcja', to='poll.Section', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='singlechoicequestionordering',
            unique_together=set([('sections', 'is_leading', 'position')]),
        ),
        migrations.AddField(
            model_name='singlechoicequestionanswer',
            name='option',
            field=models.ForeignKey(verbose_name=b'odpowied\xc5\xba', blank=True, to='poll.Option', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlechoicequestionanswer',
            name='question',
            field=models.ForeignKey(verbose_name=b'pytanie', to='poll.SingleChoiceQuestion', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlechoicequestionanswer',
            name='saved_ticket',
            field=models.ForeignKey(verbose_name=b'zapisany bilet', to='poll.SavedTicket', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlechoicequestionanswer',
            name='section',
            field=models.ForeignKey(verbose_name=b'sekcja', to='poll.Section', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlechoicequestion',
            name='options',
            field=models.ManyToManyField(to='poll.Option', verbose_name=b'odpowiedzi'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singlechoicequestion',
            name='sections',
            field=models.ManyToManyField(to='poll.Section', verbose_name=b'sekcje', through='poll.SingleChoiceQuestionOrdering'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectionordering',
            name='poll',
            field=models.ForeignKey(verbose_name=b'ankieta', to='poll.Poll', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectionordering',
            name='section',
            field=models.ForeignKey(verbose_name=b'sekcja', to='poll.Section', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sectionordering',
            unique_together=set([('poll', 'position')]),
        ),
        migrations.AddField(
            model_name='section',
            name='poll',
            field=models.ManyToManyField(to='poll.Poll', verbose_name=b'ankieta', through='poll.SectionOrdering'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='savedticket',
            name='poll',
            field=models.ForeignKey(verbose_name=b'ankieta', to='poll.Poll', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='savedticket',
            unique_together=set([('ticket', 'poll')]),
        ),
        migrations.AddField(
            model_name='poll',
            name='author',
            field=models.ForeignKey(related_name='author', verbose_name=b'autor', to='users.Employee', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='poll',
            name='group',
            field=models.ForeignKey(verbose_name=b'grupa', blank=True, to='courses.Group', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='poll',
            name='origin',
            field=models.ForeignKey(default=None, blank=True, to='poll.Origin', null=True, verbose_name=b'zbi\xc3\xb3r', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='poll',
            name='semester',
            field=models.ForeignKey(verbose_name=b'semestr', to='courses.Semester', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='poll',
            name='studies_type',
            field=models.ForeignKey(verbose_name=b'typ studi\xc3\xb3w', blank=True, to='users.Program', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='openquestionordering',
            name='question',
            field=models.ForeignKey(verbose_name=b'pytanie', to='poll.OpenQuestion', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='openquestionordering',
            name='sections',
            field=models.ForeignKey(verbose_name=b'sekcja', to='poll.Section', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='openquestionordering',
            unique_together=set([('sections', 'position')]),
        ),
        migrations.AddField(
            model_name='openquestionanswer',
            name='question',
            field=models.ForeignKey(verbose_name=b'pytanie', to='poll.OpenQuestion', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='openquestionanswer',
            name='saved_ticket',
            field=models.ForeignKey(verbose_name=b'zapisany bilet', to='poll.SavedTicket', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='openquestionanswer',
            name='section',
            field=models.ForeignKey(verbose_name=b'sekcja', to='poll.Section', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='openquestion',
            name='sections',
            field=models.ManyToManyField(to='poll.Section', verbose_name=b'sekcje', through='poll.OpenQuestionOrdering'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multiplechoicequestionordering',
            name='question',
            field=models.ForeignKey(verbose_name=b'pytanie', to='poll.MultipleChoiceQuestion', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multiplechoicequestionordering',
            name='sections',
            field=models.ForeignKey(verbose_name=b'sekcja', to='poll.Section', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='multiplechoicequestionordering',
            unique_together=set([('sections', 'position')]),
        ),
        migrations.AddField(
            model_name='multiplechoicequestionanswer',
            name='options',
            field=models.ManyToManyField(to='poll.Option', null=True, verbose_name=b'odpowiedzi', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multiplechoicequestionanswer',
            name='question',
            field=models.ForeignKey(verbose_name=b'pytanie', to='poll.MultipleChoiceQuestion', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multiplechoicequestionanswer',
            name='saved_ticket',
            field=models.ForeignKey(verbose_name=b'zapisany bilet', to='poll.SavedTicket', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multiplechoicequestionanswer',
            name='section',
            field=models.ForeignKey(verbose_name=b'sekcja', to='poll.Section', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='options',
            field=models.ManyToManyField(to='poll.Option', verbose_name=b'odpowiedzi'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='sections',
            field=models.ManyToManyField(to='poll.Section', verbose_name=b'sekcje', through='poll.MultipleChoiceQuestionOrdering'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lastvisit',
            name='poll',
            field=models.ForeignKey(to='poll.Poll', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lastvisit',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='lastvisit',
            unique_together=set([('poll', 'user')]),
        ),
    ]
