# Generated by Django 3.0.6 on 2020-05-04 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_markdown'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='category',
        ),
        migrations.AddField(
            model_name='news',
            name='priority',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Ukryte'), (1, 'Niskie'), (2, 'Normalne'), (3, 'Wysokie')], default=2, help_text='\n            <dl>\n            <dt>Ukryte</dt>\n            <dd>Wiadomość nie zostanie opublikowana;</dd>\n            <dt>Niskie</dt>\n            <dd>Wiadomość zostanie opublikowana na stronie, ale powiadomienia\n            nie będą wysłane;\n            <dt>Normalne</dt>\n            <dd>Powiadomienia będą wysłane zgodnie z preferencjami użytkowników</dd>\n            <dt>Wysokie</dt>\n            <dd>Powiadomienia otrzymają wszyscy aktywni studenci niezależnie od\n            swoich preferencji.</dd>\n            <dl>\n            <b>Uwaga:</b> Powiadomienia są wysyłane tylko dla nowych ogłoszeń, \n            nie dla zmodyfikowanych.\n        ', verbose_name='priorytet'),
        ),
        migrations.AlterField(
            model_name='news',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]