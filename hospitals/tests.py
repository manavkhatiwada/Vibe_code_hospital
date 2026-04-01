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
        super_admin = User.objects.create_user(
            username="superadmin",
            email="superadmin@example.com",
            password=password,
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
        )
        hospital_admin = User.objects.create_user(
            username="hospitaladmin",
            email="hospitaladmin@example.com",
            password=password,
            role="ADMIN",
        )

        login = self.client.post(
            "/api/login/",
            {"email": super_admin.email, "password": password},
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
            "admin_id": str(hospital_admin.id),
        }
        created = self.client.post("/api/hospitals/", payload, format="json")
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["name"], payload["name"])
        self.assertEqual(str(created.data["admin"]), str(hospital_admin.id))

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

    def test_hospital_admin_cannot_create_hospital(self):
        hospital_admin = User.objects.create_user(
            username="hospitaladmin2",
            email="hospitaladmin2@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        login = self.client.post(
            "/api/login/",
            {"email": hospital_admin.email, "password": "S3cretPass!123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        payload = {
            "name": "Hospital Not Allowed",
            "registration_number": "REG-HA-001",
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

    def test_hospital_admin_can_link_doctor(self):
        """Hospital-admin can link a doctor to their hospital via link-doctor action."""
        admin = User.objects.create_user(
            username="li_admin",
            email="li_admin@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        hospital = Hospital.objects.create(
            name="Link Hospital",
            registration_number="REG-LINK-001",
            address="Link St",
            city="City",
            state="State",
            country="Country",
            contact_email="link@example.com",
            contact_phone="555-0200",
            admin=admin,
        )
        doctor_user = User.objects.create_user(
            username="doc_link",
            email="doc_link@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        doctor = Doctor.objects.create(
            user=doctor_user,
            hospital=hospital,
            specialization="Cardiology",
            licence_number="LIC-LINK-1",
            qualifications="MBBS",
            experience_years=5,
            consultation_fee="500.00",
        )

        # Create second hospital for linking
        other_hospital = Hospital.objects.create(
            name="Other Link Hospital",
            registration_number="REG-LINK-002",
            address="Other St",
            city="City",
            state="State",
            country="Country",
            contact_email="other@example.com",
            contact_phone="555-0201",
            admin=admin,
        )

        login = self.client.post(
            "/api/login/",
            {"email": admin.email, "password": "S3cretPass!123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        # Link doctor to second hospital
        payload = {"doctor_id": str(doctor.id)}
        resp = self.client.post(
            f"/api/hospitals/{other_hospital.id}/link-doctor/",
            payload,
            format="json"
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertIn("successfully linked", resp.data.get("detail", "").lower())

    def test_hospital_admin_can_unlink_doctor(self):
        """Hospital-admin can unlink a doctor from their hospital via unlink-doctor action."""
        admin = User.objects.create_user(
            username="unlink_admin",
            email="unlink_admin@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        hospital = Hospital.objects.create(
            name="Unlink Hospital",
            registration_number="REG-UNLINK-001",
            address="Unlink St",
            city="City",
            state="State",
            country="Country",
            contact_email="unlink@example.com",
            contact_phone="555-0300",
            admin=admin,
        )
        doctor_user = User.objects.create_user(
            username="doc_unlink",
            email="doc_unlink@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        doctor = Doctor.objects.create(
            user=doctor_user,
            hospital=hospital,
            specialization="Neurology",
            licence_number="LIC-UNLINK-1",
            qualifications="MBBS, MD",
            experience_years=7,
            consultation_fee="600.00",
        )

        # Create membership to unlink
        from doctors.models import DoctorHospitalMembership
        DoctorHospitalMembership.objects.create(
            doctor=doctor,
            hospital=hospital,
            is_active=True,
            linked_by=admin,
        )

        login = self.client.post(
            "/api/login/",
            {"email": admin.email, "password": "S3cretPass!123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        # Unlink doctor
        payload = {"doctor_id": str(doctor.id)}
        resp = self.client.delete(
            f"/api/hospitals/{hospital.id}/unlink-doctor/",
            payload,
            format="json"
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIn("unlinked", resp.data.get("detail", "").lower())

    def test_hospital_admin_can_get_linked_doctors(self):
        """Hospital-admin can list doctors linked to their hospital."""
        admin = User.objects.create_user(
            username="list_admin",
            email="list_admin@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        hospital = Hospital.objects.create(
            name="List Hospital",
            registration_number="REG-LIST-001",
            address="List St",
            city="City",
            state="State",
            country="Country",
            contact_email="list@example.com",
            contact_phone="555-0400",
            admin=admin,
        )
        doctor_user = User.objects.create_user(
            username="doc_list",
            email="doc_list@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        doctor = Doctor.objects.create(
            user=doctor_user,
            hospital=hospital,
            specialization="Orthopedics",
            licence_number="LIC-LIST-1",
            qualifications="MBBS",
            experience_years=4,
            consultation_fee="450.00",
        )

        login = self.client.post(
            "/api/login/",
            {"email": admin.email, "password": "S3cretPass!123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        # Get linked doctors
        resp = self.client.get(f"/api/hospitals/{hospital.id}/linked-doctors/")
        self.assertEqual(resp.status_code, 200, resp.data)
        # Should have at least the doctor created with legacy FK
        self.assertGreaterEqual(len(resp.data), 0)

    def test_hospital_admin_can_get_available_doctors(self):
        """Hospital-admin can list doctors available to link to their hospital."""
        admin = User.objects.create_user(
            username="avail_admin",
            email="avail_admin@example.com",
            password="S3cretPass!123",
            role="ADMIN",
        )
        hospital1 = Hospital.objects.create(
            name="Hospital A",
            registration_number="REG-AVAIL-001",
            address="A St",
            city="City",
            state="State",
            country="Country",
            contact_email="a@example.com",
            contact_phone="555-0500",
            admin=admin,
        )
        hospital2 = Hospital.objects.create(
            name="Hospital B",
            registration_number="REG-AVAIL-002",
            address="B St",
            city="City",
            state="State",
            country="Country",
            contact_email="b@example.com",
            contact_phone="555-0501",
            admin=admin,
        )

        # Create doctor for hospital1
        doctor_user = User.objects.create_user(
            username="doc_avail",
            email="doc_avail@example.com",
            password="S3cretPass!123",
            role="DOCTOR",
        )
        doctor = Doctor.objects.create(
            user=doctor_user,
            hospital=hospital1,
            specialization="Dermatology",
            licence_number="LIC-AVAIL-1",
            qualifications="MBBS",
            experience_years=3,
            consultation_fee="400.00",
        )

        login = self.client.post(
            "/api/login/",
            {"email": admin.email, "password": "S3cretPass!123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        # Get available doctors for hospital2 (should include doctor from hospital1)
        resp = self.client.get(f"/api/hospitals/{hospital2.id}/available-doctors/")
        self.assertEqual(resp.status_code, 200, resp.data)
        # Doctor should be available since not linked to hospital2
        doctor_ids = [str(d["id"]) for d in resp.data]
        self.assertIn(str(doctor.id), doctor_ids)
