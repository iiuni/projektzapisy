from django.contrib.auth.models import User
from django.db import models


class NotificationPreferencesStudent(models.Model):
    user = models.OneToOneField(
        User, verbose_name="użytkownik", on_delete=models.CASCADE)
    pulled_from_queue = models.BooleanField(
        "Zapisanie Cię do grupy", default=False)
    not_pulled_from_queue = models.BooleanField("Niepowodzenie wciągnięcia Cię do grupy",
                                                default=False)
    added_new_group = models.BooleanField(
        "Dodanie nowej grupy przedmiotu, na który jesteś zapisany/a", default=False)
    teacher_has_been_changed_enrolled = models.BooleanField(
        "Zmiana prowadzącego grupy, do której jesteś zapisany/a", default=True)
    teacher_has_been_changed_queued = models.BooleanField(
        "Zmiana prowadzącego grupy, do której czekasz w kolejce", default=True)
    news_has_been_added = models.BooleanField(
        "Nowa wiadomość w Aktualnościach", default=True)
    event_decision = models.BooleanField("Decyzja w sprawie zgłoszonego przez Ciebie wydarzenia", default=True)

    @property
    def news_has_been_added_high_priority(self):
        """High-priority news is sent to all active students."""
        return self.user.student.is_active

    @property
    def thesis_has_been_accepted(self):
        return True


class NotificationPreferencesTeacher(models.Model):
    user = models.OneToOneField(
        User, verbose_name='użytkownik', on_delete=models.CASCADE)
    assigned_to_new_group_as_teacher = models.BooleanField(
        "Przydzielenie do grupy", default=True)
    news_has_been_added = models.BooleanField(
        "Nowa wiadomość w Aktualnościach", default=True)
    thesis_has_been_accepted = models.BooleanField(
        "Powiadomienie o akceptacji tematu pracy dyplomowej", default=True)
    thesis_voting_has_been_activated = models.BooleanField(
        "Powiadomienie o głosowaniu (dotyczy członka Komisji Prac Dyplomowych)", default=True)

    event_decision = models.BooleanField("Decyzja w sprawie zgłoszonego przez Ciebie wydarzenia", default=True)

    @property
    def news_has_been_added_high_priority(self):
        """Use regular news setting for employees."""
        return self.news_has_been_added
