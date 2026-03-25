from rest_framework.test import APITestCase

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
            role="HOSPITAL",
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
