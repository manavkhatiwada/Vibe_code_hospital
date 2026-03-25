from rest_framework.test import APITestCase

from hospitals.models import Hospital
from doctors.models import Doctor
from users.models import User
from .models import Appointment


class AppointmentApiTests(APITestCase):
    def setUp(self):
        self.hospital_admin = User.objects.create_user(
            username="hadmin2",
            email="hadmin2@example.com",
            password="S3cretPass!123",
            role="HOSPITAL",
        )
        self.hospital = Hospital.objects.create(
            name="Test Hospital",
            registration_number="REG-200",
            address="200 Street",
            city="City",
            state="State",
            country="Country",
            contact_email="th@example.com",
            contact_phone="555-0200",
            admin=self.hospital_admin,
        )
        self.doctor_user = User.objects.create_user(
            username="doc2",
            email="doc2@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            hospital=self.hospital,
            specialization="Dermatology",
            licence_number="LIC-222",
            qualifications="MBBS",
            experience_years=3,
            consulataion_fee="250.00",
        )

        self.patient1 = User.objects.create_user(
            username="patA",
            email="patA@example.com",
            password="S3cretPass!123",
            role="PATIENT",
        )
        self.patient2 = User.objects.create_user(
            username="patB",
            email="patB@example.com",
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

    def test_requires_auth(self):
        resp = self.client.get("/api/appointments/")
        self.assertEqual(resp.status_code, 401)

    def test_book_list_and_filter_by_logged_in_user(self):
        # Patient1 books an appointment
        self._login(self.patient1.email, "S3cretPass!123")
        payload = {
            "doctor": str(self.doctor.id),
            "hospital": str(self.hospital.id),
            "appointment_datetime": "2030-01-01T10:00:00Z",
            "reason": "Checkup",
        }
        created = self.client.post("/api/appointments/", payload, format="json")
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["status"], "PENDING")

        # Create another appointment for patient2 directly in DB
        Appointment.objects.create(
            patient=self.patient2,
            doctor=self.doctor,
            hospital=self.hospital,
            appintment_datetime="2030-01-02T10:00:00Z",
            reason="Other",
            status="PENDING",
        )

        listed = self.client.get("/api/appointments/")
        self.assertEqual(listed.status_code, 200, listed.data)
        self.assertEqual(len(listed.data), 1)
        self.assertEqual(str(listed.data[0]["patient"]), str(self.patient1.id))

    def test_cancel_endpoint(self):
        self._login(self.patient1.email, "S3cretPass!123")
        appt = Appointment.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            hospital=self.hospital,
            appintment_datetime="2030-01-03T10:00:00Z",
            reason="Cancel me",
            status="PENDING",
        )

        resp = self.client.put(f"/api/appointments/{appt.ID}/cancel/", {}, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["status"], "CANCELLED")
