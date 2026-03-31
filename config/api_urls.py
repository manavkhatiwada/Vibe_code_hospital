from django.urls import include, path
from rest_framework.routers import DefaultRouter

from doctors.views import DoctorViewSet
from hospitals.views import HospitalViewSet
from appointments.views import AppointmentViewSet
from medical_records.views import MedicalRecordViewSet

router = DefaultRouter()
router.register(r"hospitals", HospitalViewSet, basename="hospital")
router.register(r"doctors", DoctorViewSet, basename="doctor")
router.register(r"appointments", AppointmentViewSet, basename="appointment")
router.register(r"records", MedicalRecordViewSet, basename="record")

urlpatterns = [
    # Non-router endpoints (register/login/profile, etc.)
    path("", include("users.urls")),
    path("", include("patients.urls")),
    path("", include("chatbot.urls")),
    path("", include("dashboard.urls")),
    # Router endpoints
    path("", include(router.urls)),
]

