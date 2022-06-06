from django.contrib import admin

from .models import Defect, DefectManager, Image

# Register your models here.
admin.site.register(Defect)
admin.site.register(DefectManager)
admin.site.register(Image)
