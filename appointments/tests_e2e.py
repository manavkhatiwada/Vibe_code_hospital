from rest_framework.test import APITestCase

from doctors.models import Doctor
from users.models import User


class PlatformE2EWorkflowTests(APITestCase):
    def setUp(self):
        self.password = "S3cretPass!123"
        self.super_admin = User.objects.create_user(
            username="platform_super",
            email="platform_super@example.com",
            password=self.password,
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
        )

    def _login(self, email, password=None):
        response = self.client.post(
            "/api/login/",
            {"email": email, "password": password or self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response.data

    def test_e2e_multi_role_journey(self):
        # 1) Super-admin creates a hospital-admin account.
        self._login(self.super_admin.email)
        hospital_admin_payload = {
            "email": "hadmin_e2e@example.com",
            "username": "hadmin_e2e",
            "password": self.password,
            "role": "ADMIN",
        }
        create_hadmin = self.client.post("/api/admin/users/", hospital_admin_payload, format="json")
        self.assertEqual(create_hadmin.status_code, 201, create_hadmin.data)
        hospital_admin_id = create_hadmin.data["id"]

        # 2) Super-admin creates a hospital bound to hospital-admin.
        hospital_payload = {
            "name": "E2E City Hospital",
            "registration_number": "REG-E2E-001",
            "address": "1 Integration Street",
            "city": "Metropolis",
            "state": "State",
            "country": "Country",
            "contact_email": "e2e-hospital@example.com",
            "contact_phone": "555-1000",
            "admin_id": hospital_admin_id,
        }
        create_hospital = self.client.post("/api/hospitals/", hospital_payload, format="json")
        self.assertEqual(create_hospital.status_code, 201, create_hospital.data)
        hospital_id = create_hospital.data["id"]

        # 3) Super-admin creates a doctor for the hospital.
        doctor_payload = {
            "email": "doctor_e2e@example.com",
            "username": "doctor_e2e",
            "password": self.password,
            "role": "DOCTOR",
            "hospital_id": hospital_id,
            "licence_number": "LIC-E2E-001",
            "qualifications": "MBBS, MD",
            "experience_years": 7,
            "consultation_fee": "900.00",
            "specialization": "Cardiology",
        }
        create_doctor = self.client.post("/api/admin/users/", doctor_payload, format="json")
        self.assertEqual(create_doctor.status_code, 201, create_doctor.data)
        doctor_user = User.objects.get(email=doctor_payload["email"])
        doctor_profile = Doctor.objects.get(user=doctor_user)

        # 4) Public patient registers.
        patient_payload = {
            "email": "patient_e2e@example.com",
            "username": "patient_e2e",
            "password": self.password,
            "role": "PATIENT",
        }
        register_patient = self.client.post("/api/register/", patient_payload, format="json")
        self.assertEqual(register_patient.status_code, 201, register_patient.data)

        # 5) Patient books appointment and uses chatbot.
        self._login(patient_payload["email"])
        browse_doctors = self.client.get("/api/doctors/")
        self.assertEqual(browse_doctors.status_code, 200, browse_doctors.data)
        self.assertTrue(any(d["id"] == str(doctor_profile.id) for d in browse_doctors.data))

        appointment_payload = {
            "doctor": str(doctor_profile.id),
            "hospital": hospital_id,
            "appointment_datetime": "2031-01-10T09:30:00Z",
            "reason": "Chest discomfort and fatigue",
        }
        create_appointment = self.client.post("/api/appointments/", appointment_payload, format="json")
        self.assertEqual(create_appointment.status_code, 201, create_appointment.data)
        appointment_id = create_appointment.data["id"]
        patient_profile_id = create_appointment.data["patient"]

        create_conversation = self.client.post("/api/chatbot/conversations/", {}, format="json")
        self.assertEqual(create_conversation.status_code, 201, create_conversation.data)
        conversation_id = create_conversation.data["id"]

        send_chat_message = self.client.post(
            f"/api/chatbot/conversations/{conversation_id}/messages/",
            {"message_text": "I have chest pressure and shortness of breath"},
            format="json",
        )
        self.assertEqual(send_chat_message.status_code, 201, send_chat_message.data)

        # 6) Hospital-admin confirms and reschedules.
        self._login("hadmin_e2e@example.com")
        confirm_appointment = self.client.put(
            f"/api/appointments/{appointment_id}/confirm/",
            {},
            format="json",
        )
        self.assertEqual(confirm_appointment.status_code, 200, confirm_appointment.data)
        self.assertEqual(confirm_appointment.data["status"], "CONFIRMED")

        reschedule_appointment = self.client.put(
            f"/api/appointments/{appointment_id}/reschedule/",
            {"appointment_datetime": "2031-01-11T11:00:00Z"},
            format="json",
        )
        self.assertEqual(reschedule_appointment.status_code, 200, reschedule_appointment.data)

        admin_stats = self.client.get("/api/dashboard/stats/")
        self.assertEqual(admin_stats.status_code, 200, admin_stats.data)
        self.assertEqual(admin_stats.data["role"], "ADMIN")
        self.assertGreaterEqual(admin_stats.data["total_doctors"], 1)
        self.assertGreaterEqual(admin_stats.data["total_appointments"], 1)

        # 7) Doctor creates a medical record linked to appointment.
        self._login("doctor_e2e@example.com")
        record_payload = {
            "patient": patient_profile_id,
            "appointment": appointment_id,
            "diagnosis": "Stable angina (initial assessment)",
            "prescription": "ECG + lipid panel + low-dose aspirin",
        }
        create_record = self.client.post("/api/records/", record_payload, format="json")
        self.assertEqual(create_record.status_code, 201, create_record.data)

        # 8) Patient sees own appointment and record data.
        self._login(patient_payload["email"])
        patient_appointments = self.client.get("/api/appointments/")
        self.assertEqual(patient_appointments.status_code, 200, patient_appointments.data)
        self.assertEqual(len(patient_appointments.data), 1)

        patient_records = self.client.get("/api/records/")
        self.assertEqual(patient_records.status_code, 200, patient_records.data)
        self.assertEqual(len(patient_records.data), 1)
        self.assertEqual(patient_records.data[0]["diagnosis"], record_payload["diagnosis"])

    def test_e2e_cross_hospital_admin_isolation(self):
        # Super-admin creates two hospital-admins and two hospitals.
        self._login(self.super_admin.email)

        ha1 = self.client.post(
            "/api/admin/users/",
            {
                "email": "ha1_e2e@example.com",
                "username": "ha1_e2e",
                "password": self.password,
                "role": "ADMIN",
            },
            format="json",
        )
        self.assertEqual(ha1.status_code, 201, ha1.data)

        ha2 = self.client.post(
            "/api/admin/users/",
            {
                "email": "ha2_e2e@example.com",
                "username": "ha2_e2e",
                "password": self.password,
                "role": "ADMIN",
            },
            format="json",
        )
        self.assertEqual(ha2.status_code, 201, ha2.data)

        hospital1 = self.client.post(
            "/api/hospitals/",
            {
                "name": "Isolation Hospital A",
                "registration_number": "REG-ISO-A",
                "address": "A Street",
                "city": "A City",
                "state": "State",
                "country": "Country",
                "contact_email": "iso-a@example.com",
                "contact_phone": "555-2001",
                "admin_id": ha1.data["id"],
            },
            format="json",
        )
        self.assertEqual(hospital1.status_code, 201, hospital1.data)

        hospital2 = self.client.post(
            "/api/hospitals/",
            {
                "name": "Isolation Hospital B",
                "registration_number": "REG-ISO-B",
                "address": "B Street",
                "city": "B City",
                "state": "State",
                "country": "Country",
                "contact_email": "iso-b@example.com",
                "contact_phone": "555-2002",
                "admin_id": ha2.data["id"],
            },
            format="json",
        )
        self.assertEqual(hospital2.status_code, 201, hospital2.data)

        doctor_created = self.client.post(
            "/api/admin/users/",
            {
                "email": "iso_doctor@example.com",
                "username": "iso_doctor",
                "password": self.password,
                "role": "DOCTOR",
                "hospital_id": hospital1.data["id"],
                "licence_number": "LIC-ISO-1",
                "qualifications": "MBBS",
                "experience_years": 4,
                "consultation_fee": "650.00",
                "specialization": "General",
            },
            format="json",
        )
        self.assertEqual(doctor_created.status_code, 201, doctor_created.data)
        doctor = Doctor.objects.get(user__email="iso_doctor@example.com")

        # Patient books at hospital A.
        register = self.client.post(
            "/api/register/",
            {
                "email": "iso_patient@example.com",
                "username": "iso_patient",
                "password": self.password,
                "role": "PATIENT",
            },
            format="json",
        )
        self.assertEqual(register.status_code, 201, register.data)

        self._login("iso_patient@example.com")
        create_appointment = self.client.post(
            "/api/appointments/",
            {
                "doctor": str(doctor.id),
                "hospital": hospital1.data["id"],
                "appointment_datetime": "2031-02-10T10:30:00Z",
                "reason": "Routine check",
            },
            format="json",
        )
        self.assertEqual(create_appointment.status_code, 201, create_appointment.data)
        appointment_id = create_appointment.data["id"]

        # Hospital-admin for hospital B cannot access/confirm hospital A appointment.
        self._login("ha2_e2e@example.com")
        blocked_confirm = self.client.put(
            f"/api/appointments/{appointment_id}/confirm/",
            {},
            format="json",
        )
        self.assertEqual(blocked_confirm.status_code, 404, blocked_confirm.data)

    def test_e2e_chatbot_role_policy(self):
        # Non-patient roles are blocked from chatbot endpoints.
        self._login(self.super_admin.email)
        blocked = self.client.get("/api/chatbot/conversations/")
        self.assertEqual(blocked.status_code, 403, blocked.data)
