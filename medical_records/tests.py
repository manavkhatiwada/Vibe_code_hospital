from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
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
            "notes": "Flu symptoms and rest advised",
            "folder_name": "Blood Report",
            "is_private": True,
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        record = MedicalRecord.objects.get(id=resp.data["id"])
        patient_profile = Patient.objects.get(user=self.patient_user)
        self.assertEqual(record.patient_id, patient_profile.id)
        self.assertEqual(record.doctor_id, self.doctor.id)
        self.assertEqual(record.notes, "Flu symptoms and rest advised")
        self.assertEqual(record.folder_name, "Blood Report")
        self.assertTrue(record.is_private)

        list_resp = self.client.get("/api/records/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_resp.data), 1)

    def test_patient_can_create_private_record_without_doctor(self):
        self._login(self.client, self.patient_user.email, "S3cretPass!123")

        payload = {
            "notes": "Private notes only",
            "folder_name": "General",
            "is_private": True,
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        record = MedicalRecord.objects.get(id=resp.data["id"])
        self.assertIsNone(record.doctor)
        self.assertEqual(record.notes, "Private notes only")
        self.assertEqual(record.folder_name, "General")
        self.assertTrue(record.is_private)

    def test_doctor_can_create_and_list_record(self):
        self._login(self.client, self.doctor_user.email, "S3cretPass!123")
        patient_profile = Patient.objects.get(user=self.patient_user)

        payload = {
            "patient": str(patient_profile.id),
            "notes": "Allergy symptoms observed",
            "folder_name": "Kidney Report",
            "is_private": False,
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        record = MedicalRecord.objects.get(id=resp.data["id"])
        self.assertEqual(record.doctor_id, self.doctor.id)
        self.assertEqual(record.patient_id, patient_profile.id)
        self.assertEqual(record.notes, "Allergy symptoms observed")
        self.assertEqual(record.folder_name, "Kidney Report")
        self.assertFalse(record.is_private)

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
            "notes": "Migraine record",
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
            "notes": "Flu record",
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, resp.data)

    def test_patient_upload_saves_report_under_selected_folder(self):
        self._login(self.client, self.patient_user.email, "S3cretPass!123")

        payload = {
            "doctor": str(self.doctor.id),
            "notes": "Blood work attached",
            "folder_name": "Blood Report",
            "report_file": SimpleUploadedFile("lab-report.pdf", b"pdf-bytes", content_type="application/pdf"),
        }
        resp = self.client.post("/api/records/", payload, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        record = MedicalRecord.objects.get(id=resp.data["id"])
        self.assertIn("medical_reports/blood-report/", record.report_file.name)

    def test_records_are_private_by_default(self):
        self._login(self.client, self.patient_user.email, "S3cretPass!123")

        payload = {
            "doctor": str(self.doctor.id),
            "notes": "Default privacy test",
            "folder_name": "General",
        }
        resp = self.client.post("/api/records/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        record = MedicalRecord.objects.get(id=resp.data["id"])
        self.assertTrue(record.is_private, "Records should be private by default")

    def test_patient_can_delete_own_record(self):
        self._login(self.client, self.patient_user.email, "S3cretPass!123")

        create_resp = self.client.post(
            "/api/records/",
            {"notes": "To be deleted", "folder_name": "Blood Report"},
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED, create_resp.data)
        record_id = create_resp.data["id"]

        delete_resp = self.client.delete(f"/api/records/{record_id}/")
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT, delete_resp.data)
        self.assertFalse(MedicalRecord.objects.filter(id=record_id).exists())

    def test_patient_cannot_delete_another_patients_record(self):
        other_patient_user = User.objects.create_user(
            username="patient4",
            email="patient4@example.com",
            password="S3cretPass!123",
            role="PATIENT",
        )
        other_patient_profile = Patient.objects.create(user=other_patient_user)
        other_record = MedicalRecord.objects.create(
            patient=other_patient_profile, notes="Not yours", folder_name="General"
        )

        self._login(self.client, self.patient_user.email, "S3cretPass!123")
        delete_resp = self.client.delete(f"/api/records/{other_record.id}/")
        self.assertEqual(delete_resp.status_code, status.HTTP_404_NOT_FOUND, delete_resp.data)
        self.assertTrue(MedicalRecord.objects.filter(id=other_record.id).exists())

    def test_doctor_cannot_delete_a_record(self):
        self._login(self.client, self.patient_user.email, "S3cretPass!123")
        create_resp = self.client.post(
            "/api/records/",
            {"doctor": str(self.doctor.id), "notes": "Visible to doctor", "is_private": False},
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED, create_resp.data)
        record_id = create_resp.data["id"]

        self._login(self.client, self.doctor_user.email, "S3cretPass!123")
        delete_resp = self.client.delete(f"/api/records/{record_id}/")
        self.assertEqual(delete_resp.status_code, status.HTTP_403_FORBIDDEN, delete_resp.data)
        self.assertTrue(MedicalRecord.objects.filter(id=record_id).exists())
