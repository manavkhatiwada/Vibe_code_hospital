from django.db import models
import uuid 
from django.conf import settings 
from hospitals.models import Hospital


class Doctor(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital,on_delete=models.CASCADE)
    hospitals = models.ManyToManyField(
        Hospital,
        through="DoctorHospitalMembership",
        related_name="linked_doctors",
        blank=True,
    )
    specialization = models.CharField(max_length=100, blank=True)
    licence_number = models.CharField(max_length=100)
    qualifications = models.TextField()
    experience_years = models.IntegerField()
    consultation_fee = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return self.user.username


class DoctorHospitalMembership(models.Model):
    id = models.BigAutoField(primary_key=True)
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="hospital_memberships",
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="doctor_memberships",
    )
    linked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_doctor_hospital_links",
    )
    is_active = models.BooleanField(default=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "hospital")

    def __str__(self):
        return f"{self.doctor.user.username} @ {self.hospital.name}"
