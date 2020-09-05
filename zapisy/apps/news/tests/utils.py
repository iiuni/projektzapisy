from datetime import datetime, timedelta
from random import randint

from apps.news.models import News, PriorityChoices
from apps.users.tests.factories import UserFactory


def generate_random_news(new=randint(1, 6), published=True):
    ns = []
    author_user = UserFactory()
    for i in range(new):
        n = News(title="news", body="news body",
                 date=datetime.now() - timedelta(days=randint(0, 6)),
                 author_id=author_user.pk)
        if not published:
            n.priority = PriorityChoices.HIDDEN
        n.save()
        ns.append(n)
    return ns
