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
            role="HOSPITAL",
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
            consulataion_fee="500.00",
        )

    def test_list_doctors(self):
        resp = self.client.get("/api/doctors/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertGreaterEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["id"], str(self.doctor.id))

    def test_get_doctor_detail(self):
        resp = self.client.get(f"/api/doctors/{self.doctor.id}/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["id"], str(self.doctor.id))
        self.assertEqual(resp.data["user_email"], self.doctor_user.email)
        self.assertEqual(resp.data["hospital"]["id"], str(self.hospital.id))
