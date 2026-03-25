from django.db import models

# Create your models here.
import uuid
from django.conf import settings
from doctors.models import Doctor
from hospitals.models import Hospital
from patients.models import Patient
from appointments.models import Appointment

class MedicalRecord(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment,on_delete=models.SET_NULL,null=True,blank=True)
    diagnosis = models.TextField()
    prescription = models.TextField()
    report_file = models.FileField(upload_to='medical_reports/',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.patient)
    