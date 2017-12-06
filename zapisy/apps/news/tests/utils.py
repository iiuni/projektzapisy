# -*- coding: utf-8 -*-

from .models import News

from datetime import datetime, timedelta
from random import randint

def generate_random_news(category,
                         new=randint(1,6),
                         old=randint(1,6)):
    ns = []
    for i in range(new):
        n = News(title="news", body="news body",
                 date=datetime.now() - timedelta(days=randint(0,6)),
                 author_id=1)
        n.category = category
        n.save()
        ns.append(n)
    for i in range(old):
        n= News(title="old news", body="news body",
                date=datetime.now() - timedelta(days=randint(8,20)),
                author_id=1)
        n.category = category
        n.save()
        ns.append(n)
    return (new, old, ns)
