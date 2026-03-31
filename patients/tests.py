from rest_framework.test import APITestCase
import datetime

from users.models import User
from .models import Patient


class PatientProfileApiTests(APITestCase):
    def test_requires_auth(self):
        resp = self.client.get("/api/patient/profile/")
        self.assertEqual(resp.status_code, 401)

    def test_get_auto_creates_profile(self):
        password = "S3cretPass!123"
        user = User.objects.create_user(
            username="pat1",
            email="pat1@example.com",
            password=password,
            role="PATIENT",
        )

        login = self.client.post(
            "/api/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        resp = self.client.get("/api/patient/profile/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(str(resp.data["user"]), str(user.id))
        self.assertTrue(Patient.objects.filter(user=user).exists())

    def test_put_updates_own_profile(self):
        password = "S3cretPass!123"
        user = User.objects.create_user(
            username="pat2",
            email="pat2@example.com",
            password=password,
            role="PATIENT",
        )

        login = self.client.post(
            "/api/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        update = self.client.put(
            "/api/patient/profile/",
            {
                "gender": "female",
                "blood_group": "O+",
                "insurance_number": "INS-123",
            },
            format="json",
        )
        self.assertEqual(update.status_code, 200, update.data)
        self.assertEqual(update.data["gender"], "female")
        self.assertEqual(update.data["blood_group"], "O+")
        self.assertEqual(update.data["insurance_number"], "INS-123")

    def test_profile_returns_derived_age_from_date_of_birth(self):
        password = "S3cretPass!123"
        user = User.objects.create_user(
            username="pat3",
            email="pat3@example.com",
            password=password,
            role="PATIENT",
        )

        patient, _ = Patient.objects.get_or_create(user=user)
        patient.date_of_birth = datetime.date(2000, 1, 1)
        patient.save(update_fields=["date_of_birth"])

        login = self.client.post(
            "/api/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        resp = self.client.get("/api/patient/profile/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIsNotNone(resp.data["age"])

    def test_doctor_cannot_access_patient_profile_endpoint(self):
        password = "S3cretPass!123"
        doctor = User.objects.create_user(
            username="doc_profile_forbidden",
            email="doc_profile_forbidden@example.com",
            password=password,
            role="DOCTOR",
        )

        login = self.client.post(
            "/api/login/",
            {"email": doctor.email, "password": password},
            format="json",
        )
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        resp = self.client.get("/api/patient/profile/")
        self.assertEqual(resp.status_code, 403, resp.data)
