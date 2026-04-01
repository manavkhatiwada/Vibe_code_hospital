from rest_framework.test import APITestCase

from appointments.models import Appointment
from doctors.models import Doctor, DoctorHospitalMembership
from hospitals.models import Hospital
from medical_records.models import MedicalRecord
from patients.models import Patient
from users.models import User


class DashboardStatsApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_stats",
            email="admin_stats@example.com",
            password="S3cretPass!123",
            role="ADMIN",
            is_staff=True,
        )
        self.hospital = Hospital.objects.create(
            admin=self.admin,
            name="Stats Hospital",
            registration_number="REG-STATS-1",
            address="Main St",
            city="City",
            state="State",
            country="Country",
            contact_email="stats@hospital.com",
            contact_phone="12345",
        )

        self.doctor_user = User.objects.create_user(
            username="doc_stats",
            email="doc_stats@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            hospital=self.hospital,
            specialization="General",
            licence_number="LIC-STATS-1",
            qualifications="MBBS",
            experience_years=3,
            consultation_fee="500.00",
        )

        self.patient_user = User.objects.create_user(
            username="pat_stats",
            email="pat_stats@example.com",
            password="S3cretPass!123",
            role="PATIENT",
        )
        self.patient = Patient.objects.create(user=self.patient_user)

        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-01T10:00:00Z",
            reason="Checkup",
            status="PENDING",
        )
        MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment=self.appointment,
            diagnosis="Flu",
            prescription="Rest",
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
        resp = self.client.get("/api/dashboard/stats/")
        self.assertEqual(resp.status_code, 401)

    def test_admin_stats(self):
        self._login(self.admin.email, "S3cretPass!123")
        resp = self.client.get("/api/dashboard/stats/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["role"], "ADMIN")
        self.assertEqual(resp.data["total_doctors"], 1)
        self.assertEqual(resp.data["total_patients"], 1)
        self.assertEqual(resp.data["total_appointments"], 1)

    def test_doctor_stats(self):
        self._login(self.doctor_user.email, "S3cretPass!123")
        resp = self.client.get("/api/dashboard/stats/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["role"], "DOCTOR")
        self.assertEqual(resp.data["assigned_patients"], 1)
        self.assertEqual(resp.data["my_appointments"], 1)
        self.assertEqual(resp.data["my_records"], 1)

    def test_patient_stats(self):
        self._login(self.patient_user.email, "S3cretPass!123")
        resp = self.client.get("/api/dashboard/stats/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["role"], "PATIENT")
        self.assertEqual(resp.data["available_doctors"], 1)
        self.assertEqual(resp.data["my_appointments"], 1)
        self.assertEqual(resp.data["my_records"], 1)

    def test_admin_stats_include_doctor_linked_by_membership(self):
        secondary_admin = User.objects.create_user(
            username="admin_stats_2",
            email="admin_stats_2@example.com",
            password="S3cretPass!123",
            role="ADMIN",
            is_staff=True,
        )
        secondary_hospital = Hospital.objects.create(
            admin=secondary_admin,
            name="Stats Secondary Hospital",
            registration_number="REG-STATS-2",
            address="Second St",
            city="City",
            state="State",
            country="Country",
            contact_email="stats2@hospital.com",
            contact_phone="67890",
        )

        DoctorHospitalMembership.objects.get_or_create(
            doctor=self.doctor,
            hospital=secondary_hospital,
            defaults={"is_active": True},
        )

        self._login(secondary_admin.email, "S3cretPass!123")
        resp = self.client.get("/api/dashboard/stats/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["total_doctors"], 1)
