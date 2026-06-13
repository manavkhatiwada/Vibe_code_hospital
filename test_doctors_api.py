import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') # Adjusted based on typical structure
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from patients.models import Patient

User = get_user_model()
try:
    patient = User.objects.get(username='manavpatient')
    print(f"User: {patient.username}, Role: {patient.role}")
    
    # Check if patient has a Patient profile
    try:
        patient_profile = Patient.objects.get(user=patient)
        print(f"Patient profile exists: {patient_profile.id}")
    except Patient.DoesNotExist:
        print(f"NO PATIENT PROFILE FOR THIS USER - creating one")
        patient_profile = Patient.objects.create(user=patient)
        print(f"Created profile: {patient_profile.id}")
    
    # Generate fresh token
    refresh = RefreshToken.for_user(patient)
    token = str(refresh.access_token)
    
    # Test API
    # Note: This assumes the server is running locally on port 8000
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get('http://127.0.0.1:8000/api/doctors/', headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        if isinstance(data, list):
            print(f"Doctor count: {len(data)}")
            if data:
                print(f"First doctor username: {data[0].get('user_username', 'N/A')}")
        else:
            print(f"Error response: {data}")
    except requests.exceptions.ConnectionError:
        print("API Error: Connection refused. Is the Django server running on port 8000?")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
