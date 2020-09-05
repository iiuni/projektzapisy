from django.contrib.syndication.views import Feed
from django.urls import reverse

from apps.schedule.models.event import Event


class Latest(Feed):

    base_title_prefix = ""
    base_title_suffix = ""

    def item_author_name(self, item):
        return item.author.get_full_name()

    def item_author_email(self, item):
        return item.author.email

    def item_pubdate(self, item):
        return item.created

    def item_description(self, item):
        return item.description

    def item_title(self, item):
        return item.title


class LatestExams(Latest):
    title = "Zapisy - egzaminy"
    description = "Egzaminy w Instytucie Informatyki UWr"

    def link(self):
        return reverse('events:session')

    def items(self):
        return Event.get_exams()[:10]

    def item_link(self, item):
        return reverse('events:session') + "#" + str(item.id)


class LatestEvents(Latest):
    title = "Zapisy - wydarzenia"
    description = "Wydarzenia w Instytucie Informatyki UWr"

    def link(self):
        return reverse('events:event_show')

    def items(self):
        return Event.get_exams()[:10]

    def item_link(self, item):
        return reverse('events:show', args=[str(item.id)])
