from rest_framework.test import APITestCase

from hospitals.models import Hospital
from doctors.models import Doctor, DoctorHospitalMembership
from patients.models import Patient
from users.models import User
from .models import Appointment


class AppointmentApiTests(APITestCase):
    def setUp(self):
        self.hospital_admin = User.objects.create_user(
            username="hadmin2",
            email="hadmin2@example.com",
            password="S3cretPass!123",
            role="ADMIN",
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
            consultation_fee="250.00",
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
        self.patient1_profile = Patient.objects.create(user=self.patient1)
        self.patient2_profile = Patient.objects.create(user=self.patient2)

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
            patient=self.patient2_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-02T10:00:00Z",
            reason="Other",
            status="PENDING",
        )

        listed = self.client.get("/api/appointments/")
        self.assertEqual(listed.status_code, 200, listed.data)
        self.assertEqual(len(listed.data), 1)
        self.assertEqual(str(listed.data[0]["patient"]), str(self.patient1_profile.id))

    def test_cancel_endpoint(self):
        self._login(self.patient1.email, "S3cretPass!123")
        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-03T10:00:00Z",
            reason="Cancel me",
            status="PENDING",
        )

        resp = self.client.put(f"/api/appointments/{appt.id}/cancel/", {}, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["status"], "CANCELLED")

    def test_doctor_cannot_book_appointment(self):
        self._login(self.doctor_user.email, "S3cretPass!123")
        payload = {
            "doctor": str(self.doctor.id),
            "hospital": str(self.hospital.id),
            "appointment_datetime": "2030-01-01T10:00:00Z",
            "reason": "Should fail",
        }
        created = self.client.post("/api/appointments/", payload, format="json")
        self.assertEqual(created.status_code, 403, created.data)

    def test_direct_update_is_forbidden(self):
        self._login(self.patient1.email, "S3cretPass!123")
        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-03T10:00:00Z",
            reason="Initial reason",
            status="PENDING",
        )

        updated = self.client.put(
            f"/api/appointments/{appt.id}/",
            {
                "doctor": str(self.doctor.id),
                "hospital": str(self.hospital.id),
                "appointment_datetime": "2030-01-03T11:00:00Z",
                "reason": "Changed",
            },
            format="json",
        )
        self.assertEqual(updated.status_code, 403, updated.data)

    def test_hospital_admin_can_see_linked_doctor_history(self):
        secondary_admin = User.objects.create_user(
            username="hadmin3",
            email="hadmin3@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        secondary_hospital = Hospital.objects.create(
            name="Linked Hospital",
            registration_number="REG-300",
            address="300 Street",
            city="City",
            state="State",
            country="Country",
            contact_email="linked@example.com",
            contact_phone="555-0300",
            admin=secondary_admin,
        )

        DoctorHospitalMembership.objects.get_or_create(
            doctor=self.doctor,
            hospital=secondary_hospital,
            defaults={"is_active": True},
        )

        Appointment.objects.create(
            patient=self.patient2_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-02-02T10:00:00Z",
            reason="Linked visibility",
            status="PENDING",
        )

        self._login(secondary_admin.email, "S3cretPass!123")
        listed = self.client.get("/api/appointments/")
        self.assertEqual(listed.status_code, 200, listed.data)
        self.assertGreaterEqual(len(listed.data), 1)

    def test_doctor_can_confirm_own_appointment(self):
        """Doctor can confirm their own PENDING appointment."""
        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-04T10:00:00Z",
            reason="Checkup",
            status="PENDING",
        )

        self._login(self.doctor_user.email, "S3cretPass!123")
        resp = self.client.put(f"/api/appointments/{appt.id}/confirm/", {}, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["status"], "CONFIRMED")

    def test_doctor_cannot_confirm_other_doctor_appointment(self):
        """Doctor cannot confirm another doctor's appointment (404 because outside their queryset)."""
        other_doctor_user = User.objects.create_user(
            username="doc_other",
            email="docother@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        other_doctor = Doctor.objects.create(
            user=other_doctor_user,
            hospital=self.hospital,
            specialization="Orthopedics",
            licence_number="LIC-333",
            qualifications="MBBS",
            experience_years=2,
            consultation_fee="300.00",
        )

        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=other_doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-05T10:00:00Z",
            reason="Checkup",
            status="PENDING",
        )

        self._login(self.doctor_user.email, "S3cretPass!123")
        resp = self.client.put(f"/api/appointments/{appt.id}/confirm/", {}, format="json")
        # Doctor can't see other doctor's appointments, so they get 404 instead of 403
        self.assertEqual(resp.status_code, 404, resp.data)

    def test_doctor_can_reschedule_own_appointment(self):
        """Doctor can reschedule their own PENDING appointment."""
        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-06T10:00:00Z",
            reason="Checkup",
            status="PENDING",
        )

        self._login(self.doctor_user.email, "S3cretPass!123")
        payload = {
            "appointment_datetime": "2030-01-07T14:00:00Z",
        }
        resp = self.client.put(f"/api/appointments/{appt.id}/reschedule/", payload, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["appointment_datetime"], "2030-01-07T14:00:00Z")

    def test_hospital_admin_can_confirm_appointment_in_own_hospital(self):
        """Hospital admin can confirm PENDING appointments in their hospital."""
        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-08T10:00:00Z",
            reason="Checkup",
            status="PENDING",
        )

        self._login(self.hospital_admin.email, "S3cretPass!123")
        resp = self.client.put(f"/api/appointments/{appt.id}/confirm/", {}, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["status"], "CONFIRMED")

    def test_hospital_admin_cannot_confirm_appointment_in_other_hospital(self):
        """Hospital admin cannot confirm appointments outside their hospital (404 because outside queryset)."""
        other_admin = User.objects.create_user(
            username="hadmin_other",
            email="hadmin_other@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        other_hospital = Hospital.objects.create(
            name="Other Hospital",
            registration_number="REG-400",
            address="400 Street",
            city="City",
            state="State",
            country="Country",
            contact_email="other@example.com",
            contact_phone="555-0400",
            admin=other_admin,
        )

        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-09T10:00:00Z",
            reason="Checkup",
            status="PENDING",
        )

        self._login(other_admin.email, "S3cretPass!123")
        resp = self.client.put(f"/api/appointments/{appt.id}/confirm/", {}, format="json")
        # Admin can't see appointments in other hospitals, so they get 404 instead of 403
        self.assertEqual(resp.status_code, 404, resp.data)

    def test_hospital_admin_can_reschedule_appointment_in_own_hospital(self):
        """Hospital admin can reschedule appointments in their hospital."""
        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-10T10:00:00Z",
            reason="Checkup",
            status="PENDING",
        )

        self._login(self.hospital_admin.email, "S3cretPass!123")
        payload = {
            "appointment_datetime": "2030-01-11T15:00:00Z",
        }
        resp = self.client.put(f"/api/appointments/{appt.id}/reschedule/", payload, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["appointment_datetime"], "2030-01-11T15:00:00Z")

    def test_cannot_confirm_already_confirmed_appointment(self):
        """Cannot confirm an appointment that is already CONFIRMED."""
        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-12T10:00:00Z",
            reason="Checkup",
            status="CONFIRMED",
        )

        self._login(self.doctor_user.email, "S3cretPass!123")
        resp = self.client.put(f"/api/appointments/{appt.id}/confirm/", {}, format="json")
        self.assertEqual(resp.status_code, 400, resp.data)
        self.assertIn("PENDING", resp.data.get("detail", "").upper())

    def test_cannot_reschedule_cancelled_appointment(self):
        """Cannot reschedule a CANCELLED appointment."""
        appt = Appointment.objects.create(
            patient=self.patient1_profile,
            doctor=self.doctor,
            hospital=self.hospital,
            appointment_datetime="2030-01-13T10:00:00Z",
            reason="Checkup",
            status="CANCELLED",
        )

        self._login(self.doctor_user.email, "S3cretPass!123")
        payload = {"appointment_datetime": "2030-01-14T10:00:00Z"}
        resp = self.client.put(f"/api/appointments/{appt.id}/reschedule/", payload, format="json")
        self.assertEqual(resp.status_code, 400, resp.data)
        self.assertIn("cancelled", resp.data.get("detail", "").lower())
