from django.db import models

# Create your models here.
import uuid 
from django.conf import settings 

class Patient(models.Model):
    id = models.UUIDField(primary_key = True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    bloood_group = models.CharField(max_length=5)
    emergency_contact_name = models.CharField(max_length=100)
    insurance_number = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username