from django.urls import path

from .views import PatientListView, PatientProfileView

urlpatterns = [
    path("patient/profile/", PatientProfileView.as_view()),
    path("patients/", PatientListView.as_view()),
]

