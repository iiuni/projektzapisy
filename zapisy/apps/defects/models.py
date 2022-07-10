from os.path import exists

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from gdstorage.storage import GoogleDriveStorage

DEFECT_MAX_NAME_SIZE = 35
DEFECT_MAX_PLACE_SIZE = 35


class StateChoices(models.IntegerChoices):
    CREATED = 0, "Zgłoszone"
    WAITING = 1, "Oczekująca"
    IN_PROGRESS = 2, "W realizacji"
    DONE = 3, "Zakończone"


class Defect(models.Model):
    name = models.CharField(max_length=DEFECT_MAX_NAME_SIZE, verbose_name='Nazwa')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification = models.DateTimeField(auto_now_add=True)
    place = models.CharField(max_length=DEFECT_MAX_PLACE_SIZE, verbose_name="Miejsce")
    description = models.TextField("Opis usterki", blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField("Stan", choices=StateChoices.choices, default=StateChoices.CREATED)
    information_from_defect_manager = models.TextField("Informacja od serwisanta", blank=True)

    def __str__(self):
        return self.name

    def get_url(self):
        return reverse('defects:show_defect', args=[str(self.id)])

    def get_status_color(self):
        color = {StateChoices.CREATED: None, StateChoices.IN_PROGRESS: None, StateChoices.WAITING: None,
                 StateChoices.DONE: "green"}[self.state]
        return f"color: {color}" if color else ''


def select_storage():
    if exists(settings.GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE):
        return GoogleDriveStorage()
    else:
        FileSystemStorage(location="defect/")


class Image(models.Model):
    image = models.ImageField(storage=select_storage, upload_to='defects')
    defect = models.ForeignKey(Defect, on_delete=models.CASCADE, null=False, blank=True)


class DefectManager(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_id.first_name + " " + self.user_id.last_name
