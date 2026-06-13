import os
import uuid

from django.db import models
from django.utils.text import slugify

from appointments.models import Appointment
from doctors.models import Doctor
from hospitals.models import Hospital
from patients.models import Patient


def medical_report_upload_path(instance, filename):
    _, extension = os.path.splitext(filename)
    folder_name = slugify((instance.folder_name or "general").strip()) or "general"
    return f"medical_reports/{folder_name}/{uuid.uuid4().hex}{extension.lower()}"

class MedicalRecord(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.SET_NULL,null=True,blank=True)
    appointment = models.ForeignKey(Appointment,on_delete=models.SET_NULL,null=True,blank=True)
    notes = models.TextField(blank=True, default="")
    folder_name = models.CharField(max_length=120, default="General")
    diagnosis = models.TextField(blank=True, default="")
    prescription = models.TextField(blank=True, default="")
    report_file = models.FileField(upload_to=medical_report_upload_path,null=True,blank=True)
    is_private = models.BooleanField(default=True, help_text="If True, only patient can see. If False, can be shared with doctors.")
    shared_with = models.ManyToManyField(Doctor, blank=True, related_name='shared_records', help_text="Doctors the patient explicitly shared this private record with.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)
    