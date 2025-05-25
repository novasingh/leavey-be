from rest_framework import serializers
from api.models import User, Role, Department
from api.serializers.role_serializer import RoleSerializer

class UserSerializer(serializers.ModelSerializer):
    role_details = RoleSerializer(source='role', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'role_details', 'department', 'manager', 
            'profile_picture', 'phone_number', 'date_joined', 
            'last_login', 'is_active', 'is_email_verified'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_email_verified']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'role', 'department', 
            'manager', 'profile_picture', 'phone_number'
        ]
    
    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role'),
            department=validated_data.get('department'),
            manager=validated_data.get('manager'),
            profile_picture=validated_data.get('profile_picture'),
            phone_number=validated_data.get('phone_number')
        )
        return user