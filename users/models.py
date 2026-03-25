from django.db import models

# Create your models here.
import uuid 
from django.db import models 
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):

    ROLE_CHOICES = (
        ('PATIENT', 'patient'),
        ('DOCTOR','doctor'),
        ('HOSPITAL','hospital'),
    )

    id = models.UUIDField(primary_key=True,default= uuid.uuid4,editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email 
    
