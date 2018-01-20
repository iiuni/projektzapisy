# -*- coding: utf-8 -*-

from models import News
from apps.users.tests.factories import UserFactory
from datetime import datetime, timedelta
from random import randint


def generate_random_news(category,
                         new=randint(1, 6),
                         old=randint(1, 6)):
    ns = []
    author_user = UserFactory()
    for i in xrange(new):
        n = News(title="news", body="news body",
                 date=datetime.now() - timedelta(days=randint(0, 6)),
                 author_id=author_user.pk)
        n.category = category
        n.save()
        ns.append(n)
    for i in xrange(old):
        n = News(title="old news", body="news body",
                 date=datetime.now() - timedelta(days=randint(8, 20)),
                 author_id=author_user.pk)
        n.category = category
        n.save()
        ns.append(n)
    return (new, old, ns)
