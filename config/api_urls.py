from django.urls import include, path
from rest_framework.routers import DefaultRouter

from doctors.views import DoctorViewSet
from hospitals.views import HospitalViewSet
from appointments.views import AppointmentViewSet

router = DefaultRouter()
router.register(r"hospitals", HospitalViewSet, basename="hospital")
router.register(r"doctors", DoctorViewSet, basename="doctor")
router.register(r"appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    # Non-router endpoints (register/login/profile, etc.)
    path("", include("users.urls")),
    path("", include("patients.urls")),
    # Router endpoints
    path("", include(router.urls)),
]

