import logging
from os.path import exists

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse
from gdstorage.storage import GoogleDriveStorage

DEFECT_MAX_NAME_SIZE = 35
DEFECT_MAX_PLACE_SIZE = 35


class StateChoices(models.IntegerChoices):
    CREATED = 0, "Zgłoszona"
    WAITING = 1, "Oczekująca"
    IN_PROGRESS = 2, "W realizacji"
    DONE = 3, "Zakończona"


class Defect(models.Model):
    name = models.CharField(max_length=DEFECT_MAX_NAME_SIZE, verbose_name='Nazwa')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification = models.DateTimeField(auto_now=True)
    place = models.CharField(max_length=DEFECT_MAX_PLACE_SIZE, verbose_name="Miejsce")
    description = models.TextField("Opis usterki", blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Osoba zgłaszająca")
    state = models.PositiveSmallIntegerField("Stan", choices=StateChoices.choices, default=StateChoices.CREATED)
    information_from_defect_manager = models.TextField("Informacja o zmianach", blank=True)

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
        logging.getLogger().error("File " + settings.GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE +
                                  " was not found. Defect service may not work properly")
        return FileSystemStorage(location="defect/")


class DefectImage(models.Model):
    image = models.ImageField(storage=select_storage, upload_to='defects')
    defect = models.ForeignKey(Defect, on_delete=models.CASCADE, null=False, blank=True)


class DefectManager(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_id.first_name + " " + self.user_id.last_name
