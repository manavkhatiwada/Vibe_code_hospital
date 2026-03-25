from django.test import TestCase

from users.models import User
from .serializers import RegisterSerializer
from rest_framework.test import APITestCase


class UserSystemTests(TestCase):
    def test_create_user_hashes_password(self):
        plain_password = "S3cretPass!123"
        user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password=plain_password,
            role="PATIENT",
        )

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password(plain_password))

    def test_register_serializer_creates_hashed_password(self):
        plain_password = "S3cretPass!123"
        serializer = RegisterSerializer(
            data={
                "email": "bob@example.com",
                "username": "bob",
                "password": plain_password,
                "role": "DOCTOR",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password(plain_password))


class RegisterApiTests(APITestCase):
    def test_register_api_creates_user_and_hashes_password(self):
        plain_password = "S3cretPass!123"
        payload = {
            "email": "carol@example.com",
            "username": "carol",
            "password": plain_password,
            "role": "PATIENT",
        }

        resp = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["email"], payload["email"])
        self.assertEqual(resp.data["username"], payload["username"])
        self.assertEqual(resp.data["role"], payload["role"])
        self.assertNotIn("password", resp.data)

        user = User.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(plain_password))


class LoginApiTests(APITestCase):
    def test_login_api_returns_access_and_refresh(self):
        password = "S3cretPass!123"
        user = User.objects.create_user(
            username="dave",
            email="dave@example.com",
            password=password,
            role="PATIENT",
        )
        self.assertTrue(user.check_password(password))

        resp = self.client.post(
            "/api/login/",
            {"email": "dave@example.com", "password": password},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)


class ProfileApiTests(APITestCase):
    def test_profile_api_requires_auth(self):
        resp = self.client.get("/api/profile/")
        self.assertEqual(resp.status_code, 401)

    def test_profile_api_returns_logged_in_user(self):
        password = "S3cretPass!123"
        user = User.objects.create_user(
            username="erin",
            email="erin@example.com",
            password=password,
            role="DOCTOR",
            phone_number="12345",
        )

        login = self.client.post(
            "/api/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        self.assertEqual(login.status_code, 200, login.data)
        access = login.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = self.client.get("/api/profile/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["email"], user.email)
        self.assertEqual(resp.data["username"], user.username)
        self.assertEqual(resp.data["role"], user.role)
        self.assertEqual(resp.data["phone_number"], user.phone_number)
