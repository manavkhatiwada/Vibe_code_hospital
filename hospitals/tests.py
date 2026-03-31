from rest_framework.test import APITestCase

from doctors.models import Doctor
from .models import Hospital
from users.models import User


class HospitalApiTests(APITestCase):
    def test_hospitals_requires_auth(self):
        resp = self.client.get("/api/hospitals/")
        self.assertEqual(resp.status_code, 401)

    def test_create_and_list_hospitals(self):
        password = "S3cretPass!123"
        user = User.objects.create_user(
            username="hospitaladmin",
            email="hospitaladmin@example.com",
            password=password,
            role="ADMIN",
        )

        login = self.client.post(
            "/api/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        self.assertEqual(login.status_code, 200, login.data)
        access = login.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        payload = {
            "name": "City Hospital",
            "registration_number": "REG-001",
            "address": "123 Main St",
            "city": "Metropolis",
            "state": "State",
            "country": "Country",
            "contact_email": "contact@cityhospital.com",
            "contact_phone": "555-0100",
        }
        created = self.client.post("/api/hospitals/", payload, format="json")
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["name"], payload["name"])
        self.assertEqual(str(created.data["admin"]), str(user.id))

        listed = self.client.get("/api/hospitals/")
        self.assertEqual(listed.status_code, 200, listed.data)
        self.assertGreaterEqual(len(listed.data), 1)

    def test_patient_cannot_create_hospital(self):
        patient = User.objects.create_user(
            username="pat_hospital",
            email="pat_hospital@example.com",
            password="S3cretPass!123",
            role="PATIENT",
        )
        login = self.client.post(
            "/api/login/",
            {"email": patient.email, "password": "S3cretPass!123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        payload = {
            "name": "Forbidden Hospital",
            "registration_number": "REG-PT-001",
            "address": "123 Main St",
            "city": "Metropolis",
            "state": "State",
            "country": "Country",
            "contact_email": "contact@forbidden.com",
            "contact_phone": "555-0100",
        }
        created = self.client.post("/api/hospitals/", payload, format="json")
        self.assertEqual(created.status_code, 403, created.data)

    def test_doctor_sees_only_own_hospital(self):
        admin = User.objects.create_user(
            username="admin_hospital_scope",
            email="admin_hospital_scope@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        hospital = Hospital.objects.create(
            name="Scoped Hospital",
            registration_number="REG-SCOPE-001",
            address="123 Main St",
            city="Metropolis",
            state="State",
            country="Country",
            contact_email="contact@scope.com",
            contact_phone="555-0100",
            admin=admin,
        )
        doctor_user = User.objects.create_user(
            username="doc_scope",
            email="doc_scope@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        Doctor.objects.create(
            user=doctor_user,
            hospital=hospital,
            specialization="General",
            licence_number="LIC-SCOPE-1",
            qualifications="MBBS",
            experience_years=2,
            consultation_fee="350.00",
        )

        login = self.client.post(
            "/api/login/",
            {"email": doctor_user.email, "password": "S3cretPass!123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        listed = self.client.get("/api/hospitals/")
        self.assertEqual(listed.status_code, 200, listed.data)
        self.assertEqual(len(listed.data), 1)
        self.assertEqual(listed.data[0]["id"], str(hospital.id))
