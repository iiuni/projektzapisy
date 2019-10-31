from django.db import migrations
from html2text import html2text as markdownify


def migrate_news_to_markdown(apps, schema_editor):
    News = apps.get_model('news', 'News')
    for news in News.objects.all():
        news.body = markdownify(news.body)
        news.save()


class Migration(migrations.Migration):
    dependencies = [
        ('news', '0002_auto_20180525_0559'),
    ]

    operations = [
        migrations.operations.RunPython(migrate_news_to_markdown),
    ]
