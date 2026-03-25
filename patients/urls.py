from django.urls import path

from .views import PatientProfileView

urlpatterns = [
    path("patient/profile/", PatientProfileView.as_view()),
]

