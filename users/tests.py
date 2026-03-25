from django.test import TestCase

from users.models import User
from .serializers import RegisterSerializer


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
