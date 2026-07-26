import os
import django
import requests
import re

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

try:
    User = get_user_model()
    user = User.objects.get(username='manavpatient')
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    headers = {'Authorization': f'Bearer {token}'}

    # Test records endpoint
    response = requests.get('http://127.0.0.1:8000/api/records/', headers=headers)
    print(f"Status: {response.status_code}")
    
    # Extract common Django error parts
    match = re.search(r"<th>Exception Value:</th>\s*<td><pre>(.*?)</pre></td>", response.text, re.DOTALL)
    if match:
        print(f"Error Detail: {match.group(1).strip()}")
    else:
        # Fallback to looking for "no such table" or similar in text
        match = re.search(r"no such table: \w+", response.text)
        if match:
             print(f"Error Detail: {match.group(0)}")
        else:
             print(f"Response (truncated): {response.text[:1000]}")
except Exception as e:
    print(f"Error: {e}")
