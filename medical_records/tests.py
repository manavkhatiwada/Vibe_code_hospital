from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from appointments.models import Appointment
from hospitals.models import Hospital
from doctors.models import Doctor
from patients.models import Patient
from users.models import User
from .models import MedicalRecord


class MedicalRecordApiTests(APITestCase):
    def _login(self, client, email, password):
        resp = client.post("/api/login/", {"email": email, "password": password}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def setUp(self):
        self.hospital_admin = User.objects.create_user(
            username="hadmin",
            email="hadmin@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        self.hospital = Hospital.objects.create(
            name="Test Hospital",
            registration_number="REG-100",
            address="1 Street",
            city="City",
            state="State",
            country="Country",
            contact_email="contact@example.com",
            contact_phone="555-0100",
            admin=self.hospital_admin,
        )

        self.doctor_user = User.objects.create_user(
            username="doctor1",
            email="doctor1@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            hospital=self.hospital,
            specialization="Dermatology",
            licence_number="LIC-1",
            qualifications="MBBS",
            experience_years=1,
            consultation_fee="100.00",
        )

        self.patient_user = User.objects.create_user(
            username="patient1",
            email="patient1@example.com",
            password="S3cretPass!123",
            role="PATIENT",
        )
        self.patient_profile = Patient.objects.create(user=self.patient_user)

        self.appointment = Appointment.objects.create(
            patient=self.patient_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-01T10:00:00Z",
            reason="Initial Consultation",
            status="PENDING",
        )

    def test_patient_can_create_and_list_record(self):
        self._login(self.client, self.patient_user.email, "S3cretPass!123")

        payload = {
            "doctor": str(self.doctor.id),
            "diagnosis": "Flu",
            "prescription": "Rest and fluids",
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        record = MedicalRecord.objects.get(id=resp.data["id"])
        patient_profile = Patient.objects.get(user=self.patient_user)
        self.assertEqual(record.patient_id, patient_profile.id)
        self.assertEqual(record.doctor_id, self.doctor.id)

        list_resp = self.client.get("/api/records/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_resp.data), 1)

    def test_doctor_can_create_and_list_record(self):
        self._login(self.client, self.doctor_user.email, "S3cretPass!123")
        patient_profile = Patient.objects.get(user=self.patient_user)

        payload = {
            "patient": str(patient_profile.id),
            "diagnosis": "Allergy",
            "prescription": "Antihistamines",
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        record = MedicalRecord.objects.get(id=resp.data["id"])
        self.assertEqual(record.doctor_id, self.doctor.id)
        self.assertEqual(record.patient_id, patient_profile.id)

        list_resp = self.client.get("/api/records/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_resp.data), 1)

    def test_doctor_cannot_create_record_for_unassigned_patient(self):
        other_patient_user = User.objects.create_user(
            username="patient2",
            email="patient2@example.com",
            password="S3cretPass!123",
            role="PATIENT",
        )
        other_patient_profile = Patient.objects.create(user=other_patient_user)

        self._login(self.client, self.doctor_user.email, "S3cretPass!123")
        payload = {
            "patient": str(other_patient_profile.id),
            "diagnosis": "Migraine",
            "prescription": "Hydration",
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, resp.data)

    def test_patient_cannot_link_someone_else_appointment(self):
        other_patient_user = User.objects.create_user(
            username="patient3",
            email="patient3@example.com",
            password="S3cretPass!123",
            role="PATIENT",
        )
        other_patient_profile = Patient.objects.create(user=other_patient_user)
        other_appointment = Appointment.objects.create(
            patient=other_patient_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-02-01T10:00:00Z",
            reason="Other Consultation",
            status="PENDING",
        )

        self._login(self.client, self.patient_user.email, "S3cretPass!123")
        payload = {
            "doctor": str(self.doctor.id),
            "appointment": str(other_appointment.id),
            "diagnosis": "Flu",
            "prescription": "Rest",
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, resp.data)
