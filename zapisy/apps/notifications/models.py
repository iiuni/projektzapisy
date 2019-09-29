from django.db import models
from django.contrib.auth.models import User


class NotificationPreferencesStudent(models.Model):
    user = models.ForeignKey(User, verbose_name="użytkownik", on_delete=models.CASCADE)
    pulled_from_queue = models.BooleanField("Zapisanie Cię do grupy", default=False)
    not_pulled_from_queue = models.BooleanField("Niepowodzenie wciągnięcia Cię do grupy",
                                                default=False)
    added_new_group = models.BooleanField(
        "Dodanie nowej grupy przedmiotu, na który jesteś zapisany/a", default=False)
    teacher_has_been_changed_enrolled = models.BooleanField(
        "Zmiana prowadzącego grupy, do której jesteś zapisany/a", default=True)
    teacher_has_been_changed_queued = models.BooleanField(
        "Zmiana prowadzącego grupy, do której czekasz w kolejce", default=True)
    news_has_been_added = models.BooleanField("Nowa wiadomość w Aktualnościach", default=True)


class NotificationPreferencesTeacher(models.Model):
    user = models.ForeignKey(User, verbose_name='użytkownik', on_delete=models.CASCADE)
    assigned_to_new_group_as_teacher = models.BooleanField("Przydzielenie do grupy", default=True)
    news_has_been_added = models.BooleanField("Nowa wiadomość w Aktualnościach", default=True)
