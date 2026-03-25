from django.db import models


import uuid 
from django.conf import settings 

class Hospital(models.Model):
    id = models.UUIDField(primary_key = True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state= models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    contact_email= models.EmailField()
    contact_phone = models.CharField(max_length = 20)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hospital_admin')

    def __str__(self):
        return self.name
    


