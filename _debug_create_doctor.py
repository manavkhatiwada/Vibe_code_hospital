import os
import django
from django.test.utils import override_settings
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from users.models import User
from hospitals.models import Hospital

password = 'S3cretPass!123'
client = APIClient()
client.raise_request_exception = True

with override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1']):
    # Reuse or create a hospital-admin and hospital similar to the UI flow.
    admin, _ = User.objects.get_or_create(
        email='debug_hadmin@example.com',
        defaults={
            'username': 'debug_hadmin',
            'role': 'ADMIN',
            'is_staff': False,
            'is_superuser': False,
        },
    )
    admin.username = 'debug_hadmin'
    admin.role = 'ADMIN'
    admin.is_staff = False
    admin.is_superuser = False
    admin.set_password(password)
    admin.save()

    hospital, _ = Hospital.objects.get_or_create(
        admin=admin,
        name='Debug Hospital',
        defaults={
            'registration_number': 'REG-DBG-1',
            'address': '1 Debug St',
            'city': 'City',
            'state': 'State',
            'country': 'Country',
            'contact_email': 'debug@hospital.com',
            'contact_phone': '555-1111',
        },
    )

    login = client.post('/api/login/', {'email': admin.email, 'password': password}, format='json')
    print('login status', login.status_code)
    print('login data', getattr(login, 'data', None))
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    payload = {
        'email': 'debugdoc@example.com',
        'username': 'debugdoc',
        'password': password,
        'role': 'DOCTOR',
        'hospital_id': str(hospital.id),
        'licence_number': 'LIC-DBG-1',
        'qualifications': 'MBBS',
        'experience_years': 4,
        'consultation_fee': '750.00',
        'specialization': 'Cardiology',
    }
    try:
        resp = client.post('/api/admin/users/', payload, format='json')
        print('create status', resp.status_code)
        print('create data', getattr(resp, 'data', None))
        print('create content', resp.content.decode('utf-8', errors='ignore'))
    except Exception:
        traceback.print_exc()
