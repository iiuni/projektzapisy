from django.contrib import admin

from .models import Defect, DefectMaintainer, Image

# Register your models here.
admin.site.register(Defect)
admin.site.register(DefectMaintainer)
admin.site.register(Image)
