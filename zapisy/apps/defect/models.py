from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from gdstorage.storage import GoogleDriveStorage

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()

DEFECT_MAX_NAME_SIZE = 255
DEFECT_MAX_PLACE_SIZE = 255
DEFECT_MAX_INFORMATION_FROM_REPAIRER_SIZE = 255


class StateChoices(models.IntegerChoices):
    CREATED = 0, "Zgłoszone"
    IN_PROGRESS = 1, "W realizacji"
    WAITING = 2, "W oczekiwaniu na realizację"
    DONE = 3, "Zakończone"


class Defect(models.Model):
    name = models.CharField(max_length=DEFECT_MAX_NAME_SIZE, verbose_name='Nazwa')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification = models.DateTimeField(auto_now_add=True)
    place = models.CharField(max_length=DEFECT_MAX_PLACE_SIZE, verbose_name="Miejsce")
    description = models.TextField("Opis usterki", blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField("Stan", choices=StateChoices.choices, default=StateChoices.CREATED)
    information_from_repairer = models.TextField("Informacja od serwisanta", blank=True)

    def get_url(self):
        return reverse('defects:show_defect', args=[str(self.id)])

    def get_status_color(self):
        color = {StateChoices.CREATED: None, StateChoices.IN_PROGRESS: None, StateChoices.WAITING: None,
                 StateChoices.DONE: "green"}[self.state]
        return f"color: {color}" if color else ''


class Image(models.Model):
    image = models.ImageField(upload_to='defect', storage=gd_storage)
    defect = models.ForeignKey(Defect, on_delete=models.CASCADE, null=False, blank=True)


class DefectMaintainer(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
