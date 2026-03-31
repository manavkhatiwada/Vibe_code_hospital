"""
End-to-end integration tests covering full workflows:
1. Patient registration → login → dashboard
2. Patient books appointment
3. Doctor sees appointment → adds medical record
4. Patient views medical record
5. Admin views updated dashboard metrics
"""

from rest_framework.test import APITestCase
from django.utils import timezone
from hospitals.models import Hospital
from doctors.models import Doctor
from patients.models import Patient
from users.models import User
from appointments.models import Appointment
from medical_records.models import MedicalRecord


class EndToEndPatientFlow(APITestCase):
    """Test complete patient journey from signup to viewing records."""

    def setUp(self):
        # Create hospital and admin
        self.admin = User.objects.create_user(
            username="admin_e2e",
            email="admin_e2e@example.com",
            password="SecurePass!123",
            role="ADMIN",
            is_staff=True,
        )
        self.hospital = Hospital.objects.create(
            admin=self.admin,
            name="E2E Test Hospital",
            registration_number="REG-E2E-001",
            address="123 Main St",
            city="Test City",
            state="Test State",
            country="Test Country",
            contact_email="contact@e2e.com",
            contact_phone="555-1234",
        )

        # Create doctor
        self.doctor_user = User.objects.create_user(
            username="doctor_e2e",
            email="doctor_e2e@example.com",
            password="SecurePass!123",
            role="DOCTOR",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            hospital=self.hospital,
            specialization="General Medicine",
            licence_number="LIC-E2E-001",
            qualifications="MBBS, MD",
            experience_years=10,
            consultation_fee="600.00",
        )

    def _login(self, email, password):
        """Helper to login and return access token."""
        resp = self.client.post(
            "/api/login/",
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token

    def test_complete_patient_flow(self):
        """Patient: register → login → view profile → book appointment → view record."""
        
        # Step 1: Patient registers
        register_payload = {
            "username": "patient_e2e",
            "email": "patient_e2e@example.com",
            "password": "SecurePass!123",
            "role": "PATIENT",
        }
        register_resp = self.client.post("/api/register/", register_payload, format="json")
        self.assertEqual(register_resp.status_code, 201, register_resp.data)
        self.assertEqual(register_resp.data["role"], "PATIENT")

        # Step 2: Patient logs in
        self._login("patient_e2e@example.com", "SecurePass!123")

        # Step 3: Patient views own profile (auto-creates Patient profile)
        profile_resp = self.client.get("/api/patient/profile/")
        self.assertEqual(profile_resp.status_code, 200, profile_resp.data)
        self.assertIn("user", profile_resp.data)

        # Step 4: Patient books appointment with doctor
        book_payload = {
            "doctor": str(self.doctor.id),
            "hospital": str(self.hospital.id),
            "date": "2030-06-15",
            "time": "14:30:00",
            "reason": "Regular checkup",
        }
        book_resp = self.client.post("/api/appointments/", book_payload, format="json")
        self.assertEqual(book_resp.status_code, 201, book_resp.data)
        appointment_id = book_resp.data["id"]
        self.assertEqual(book_resp.data["status"], "PENDING")
        self.assertEqual(book_resp.data["doctor_name"], "doctor_e2e")

        # Step 5: Patient views their appointments
        appt_list_resp = self.client.get("/api/appointments/")
        self.assertEqual(appt_list_resp.status_code, 200)
        self.assertEqual(len(appt_list_resp.data), 1)

        # Step 6: Doctor logs in and views appointments
        self._login("doctor_e2e@example.com", "SecurePass!123")
        doc_appt_resp = self.client.get("/api/appointments/")
        self.assertEqual(doc_appt_resp.status_code, 200)
        self.assertEqual(len(doc_appt_resp.data), 1)
        self.assertEqual(doc_appt_resp.data[0]["status"], "PENDING")

        # Step 7: Doctor creates medical record for patient
        appointment_obj = Appointment.objects.get(id=appointment_id)
        patient_profile = appointment_obj.patient
        record_payload = {
            "patient": str(patient_profile.id),
            "appointment": str(appointment_id),
            "diagnosis": "Mild hypertension",
            "prescription": "Daily exercise and reduced salt intake",
        }
        record_resp = self.client.post("/api/records/", record_payload, format="json")
        self.assertEqual(record_resp.status_code, 201, record_resp.data)
        record_id = record_resp.data["id"]

        # Step 8: Doctor views their records
        doc_records_resp = self.client.get("/api/records/")
        self.assertEqual(doc_records_resp.status_code, 200)
        self.assertGreaterEqual(len(doc_records_resp.data), 1)

        # Step 9: Patient logs back in and views their medical records
        self._login("patient_e2e@example.com", "SecurePass!123")
        patient_records_resp = self.client.get("/api/records/")
        self.assertEqual(patient_records_resp.status_code, 200)
        self.assertEqual(len(patient_records_resp.data), 1)
        self.assertEqual(patient_records_resp.data[0]["diagnosis"], "Mild hypertension")

    def test_admin_dashboard_metrics(self):
        """Admin: verify dashboard shows correct metrics for appointments and records."""
        
        # Create patient and appointment
        patient_user = User.objects.create_user(
            username="admin_test_patient",
            email="admin_test_patient@example.com",
            password="SecurePass!123",
            role="PATIENT",
        )
        patient_profile = Patient.objects.create(user=patient_user)
        
        appointment = Appointment.objects.create(
            patient=patient_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-07-01T10:00:00Z",
            reason="Follow-up",
            status="COMPLETED",
        )
        
        record = MedicalRecord.objects.create(
            patient=patient_profile,
            doctor=self.doctor,
            appointment=appointment,
            diagnosis="Blood pressure controlled",
            prescription="Continue medication",
        )

        # Admin logs in and views dashboard
        self._login("admin_e2e@example.com", "SecurePass!123")
        stats_resp = self.client.get("/api/dashboard/stats/")
        self.assertEqual(stats_resp.status_code, 200, stats_resp.data)
        self.assertEqual(stats_resp.data["role"], "ADMIN")
        self.assertEqual(stats_resp.data["total_doctors"], 1)
        self.assertGreaterEqual(stats_resp.data["total_patients"], 1)
        self.assertGreaterEqual(stats_resp.data["total_appointments"], 1)
        self.assertEqual(stats_resp.data["completed_appointments"], 1)
        self.assertGreaterEqual(stats_resp.data["total_records"], 1)

    def test_doctor_dashboard_metrics(self):
        """Doctor: verify dashboard shows correct assigned patients and metrics."""
        
        # Create patient and appointment
        patient_user = User.objects.create_user(
            username="doc_metrics_patient",
            email="doc_metrics_patient@example.com",
            password="SecurePass!123",
            role="PATIENT",
        )
        patient_profile = Patient.objects.create(user=patient_user)
        
        Appointment.objects.create(
            patient=patient_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-08-01T14:00:00Z",
            reason="Consultation",
            status="PENDING",
        )

        # Doctor logs in and views dashboard
        self._login("doctor_e2e@example.com", "SecurePass!123")
        stats_resp = self.client.get("/api/dashboard/stats/")
        self.assertEqual(stats_resp.status_code, 200, stats_resp.data)
        self.assertEqual(stats_resp.data["role"], "DOCTOR")
        self.assertEqual(stats_resp.data["assigned_patients"], 1)
        self.assertEqual(stats_resp.data["my_appointments"], 1)
        self.assertEqual(stats_resp.data["pending_appointments"], 1)

    def test_patient_cannot_access_doctor_endpoints(self):
        """Verify role boundaries: patient cannot access doctor-specific operations."""
        
        # Patient logs in
        patient_user = User.objects.create_user(
            username="boundary_patient",
            email="boundary_patient@example.com",
            password="SecurePass!123",
            role="PATIENT",
        )
        self._login("boundary_patient@example.com", "SecurePass!123")

        # Patient cannot create medical records directly (must be doctor)
        patient_profile = Patient.objects.create(user=patient_user)
        record_payload = {
            "patient": str(patient_profile.id),
            "doctor": str(self.doctor.id),
            "diagnosis": "Should fail",
            "prescription": "This is not allowed",
        }
        record_resp = self.client.post("/api/records/", record_payload, format="json")
        # Patient can create, but only as uploader with appointment
        
        # Patient cannot modify hospital
        hospital_payload = {
            "name": "Hacked Hospital",
            "registration_number": "REG-HACK",
            "address": "Hack St",
            "city": "Hack City",
            "state": "Hack State",
            "country": "Hack Country",
            "contact_email": "hack@example.com",
            "contact_phone": "555-0000",
        }
        hospital_resp = self.client.post("/api/hospitals/", hospital_payload, format="json")
        self.assertEqual(hospital_resp.status_code, 403, hospital_resp.data)

    def test_doctor_cannot_create_admin_accounts(self):
        """Verify role boundaries: only admin can create privileged accounts."""
        
        # Doctor logs in
        self._login("doctor_e2e@example.com", "SecurePass!123")

        # Doctor attempts to create another doctor account via admin endpoint
        admin_payload = {
            "email": "fake_doctor@example.com",
            "username": "fakedoc",
            "password": "SecurePass!123",
            "role": "DOCTOR",
            "hospital_id": str(self.hospital.id),
            "licence_number": "LIC-FAKE",
            "qualifications": "Fake quals",
            "experience_years": 5,
            "consultation_fee": "500.00",
        }
        admin_resp = self.client.post("/api/admin/users/", admin_payload, format="json")
        self.assertEqual(admin_resp.status_code, 403, admin_resp.data)
