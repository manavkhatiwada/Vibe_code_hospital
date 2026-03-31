from django.db import models
import uuid 
from django.conf import settings 
from hospitals.models import Hospital

class Doctor(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital,on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True)
    licence_number = models.CharField(max_length=100)
    qualifications = models.TextField()
    experience_years = models.IntegerField()
    consultation_fee = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return self.user.username
