from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProfileSerializer, RegisterSerializer
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    POST /api/login/

    Returns:
    - access: JWT access token
    - refresh: JWT refresh token

    Note: since `User.USERNAME_FIELD = "email"`, SimpleJWT expects `email` + `password`.
    """
    pass


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)