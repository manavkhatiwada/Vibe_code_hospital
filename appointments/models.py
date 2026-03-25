from django.db import models

# Create your models here.
from django.db import models 
from django.conf import settings
import uuid
from doctors.models import Doctor
from hospitals.models import Hospital

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING','Pending'),
        ('CONFIRMED','Confirmed'),
        ('CANCELLED','Cancelled'),
        ('COMPLETED','Completed'),
    ]

    ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital,on_delete=models.CASCADE)
    appintment_datetime =  models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    reason = models.TextField()

    def __str__(self):
        return f"{self.patient} - {self.doctor}"