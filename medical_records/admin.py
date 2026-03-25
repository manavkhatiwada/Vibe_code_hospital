from django.contrib import admin

# Register your models here.
from .models import MedicalRecord
admin.site.register(MedicalRecord)