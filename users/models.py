import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):

    ROLE_CHOICES = (
        ('PATIENT', 'patient'),
        ('DOCTOR','doctor'),
        ('ADMIN','admin'),
    )

    id = models.UUIDField(primary_key=True,default= uuid.uuid4,editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    # When `USERNAME_FIELD` is `email`, Django's `createsuperuser` command will
    # prompt only for `REQUIRED_FIELDS` besides the email + password.
    REQUIRED_FIELDS = ["username", "role"]

    @property
    def name(self):
        # Keep compatibility with UI/business language that uses `name`.
        return self.username

    def __str__(self):
        return self.email 
    
