from rest_framework import serializers
from .models import users

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ['email','username','password','role']
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        user = users.objects.create_user(validated_data['email'],validated_data['username'],validated_data['password'],validated_data['role'])
        return user