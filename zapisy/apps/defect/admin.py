from django.contrib import admin

from .models import Defect, DefectMaintainer

# Register your models here.
admin.site.register(Defect)
admin.site.register(DefectMaintainer)
