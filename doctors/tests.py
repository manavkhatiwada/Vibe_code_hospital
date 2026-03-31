from rest_framework.test import APITestCase

from hospitals.models import Hospital
from users.models import User
from .models import Doctor


class DoctorApiTests(APITestCase):
    def setUp(self):
        self.hospital_admin = User.objects.create_user(
            username="hadmin",
            email="hadmin@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        self.hospital = Hospital.objects.create(
            name="General Hospital",
            registration_number="REG-999",
            address="1 Street",
            city="City",
            state="State",
            country="Country",
            contact_email="gh@example.com",
            contact_phone="555-0000",
            admin=self.hospital_admin,
        )
        self.doctor_user = User.objects.create_user(
            username="doc1",
            email="doc1@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            hospital=self.hospital,
            specialization="Cardiology",
            licence_number="LIC-123",
            qualifications="MBBS",
            experience_years=5,
            consultation_fee="500.00",
        )
        self.patient_user = User.objects.create_user(
            username="pat_doc_tests",
            email="pat_doc_tests@example.com",
            password="S3cretPass!123",
            role="PATIENT",
        )

    def _login(self, email, password):
        resp = self.client.post(
            "/api/login/",
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_requires_auth_for_list(self):
        resp = self.client.get("/api/doctors/")
        self.assertEqual(resp.status_code, 401)

    def test_patient_can_list_doctors(self):
        self._login(self.patient_user.email, "S3cretPass!123")
        resp = self.client.get("/api/doctors/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertGreaterEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["id"], str(self.doctor.id))

    def test_get_doctor_detail_requires_auth(self):
        resp = self.client.get(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(resp.status_code, 401)

    def test_admin_can_delete_doctor(self):
        self._login(self.hospital_admin.email, "S3cretPass!123")
        resp = self.client.delete(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(resp.status_code, 204, resp.data)

    def test_patient_cannot_delete_doctor(self):
        self._login(self.patient_user.email, "S3cretPass!123")
        resp = self.client.delete(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(resp.status_code, 403, resp.data)

    def test_patient_can_get_doctor_detail(self):
        self._login(self.patient_user.email, "S3cretPass!123")
        resp = self.client.get(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["id"], str(self.doctor.id))
        self.assertEqual(resp.data["user_email"], self.doctor_user.email)
        self.assertEqual(resp.data["hospital"]["id"], str(self.hospital.id))
