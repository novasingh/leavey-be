from rest_framework import status, permissions, viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta
import requests
import uuid

# Consolidated imports for models
from .models import (
    User, Role, Department, Event,
    LeaveType, LeaveRequest, LeaveSummary, LeaveApproval, LeaveSetting
)

# Consolidated imports for serializers
from .serializers.user_serializer import UserSerializer, UserCreateSerializer, ManagerListSerializer
from .serializers.role_serializer import RoleSerializer
from .serializers.department_serializer import DepartmentSerializer
from .serializers.event_serializer import EventSerializer
from .serializers.leave_serializer import (
    LeaveTypeSerializer, LeaveRequestSerializer, LeaveSummarySerializer,
    LeaveApprovalSerializer, LeaveSettingSerializer
)

from .utils.emails import send_verification_email, send_password_reset_email



# Authentication Views
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=UserCreateSerializer,
        responses={
            201: UserSerializer,
            400: "Bad Request"
        },
        operation_description="Register a new user"
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate verification token
            token = str(uuid.uuid4())
            user.reset_password_token = token
            user.reset_password_expires = timezone.now() + timedelta(days=1)
            user.save()
            
            # Send verification email
            verification_url = f"{request.scheme}://{request.get_host()}/api/auth/verify-email?token={token}"
            send_verification_email(user, verification_url)
            
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
            400: "Bad Request",
            401: "Unauthorized"
        },
        operation_description="Login with email and password"
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({'error': 'User account is disabled'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Update last login
        user.last_login = timezone.now()
        user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_QUERY, description="Verification token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: "Email verified successfully",
            400: "Invalid token"
        },
        operation_description="Verify email with token"
    )
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(
                reset_password_token=token,
                reset_password_expires__gt=timezone.now()
            )
        except User.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_email_verified = True
        user.reset_password_token = None
        user.reset_password_expires = None
        user.save()
        
        return Response({'message': 'Email verified successfully'})

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            }
        ),
        responses={
            200: "Password reset email sent",
            400: "Bad Request"
        },
        operation_description="Request password reset"
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            return Response({'message': 'Password reset email sent if account exists'})
        
        # Generate reset token
        token = str(uuid.uuid4())
        user.reset_password_token = token
        user.reset_password_expires = timezone.now() + timedelta(hours=1)
        user.save()
        
        # Send reset email
        reset_url = f"{request.scheme}://{request.get_host()}/reset-password?token={token}"
        send_password_reset_email(user, reset_url)
        
        return Response({'message': 'Password reset email sent'})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['token', 'password', 'confirm_password'],
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            }
        ),
        responses={
            200: "Password reset successful",
            400: "Bad Request"
        },
        operation_description="Reset password with token"
    )
    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if not token or not password or not confirm_password:
            return Response({'error': 'Token, password and confirm_password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(
                reset_password_token=token,
                reset_password_expires__gt=timezone.now()
            )
        except User.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset password
        user.set_password(password)
        user.reset_password_token = None
        user.reset_password_expires = None
        user.save()
        
        return Response({'message': 'Password reset successful'})

class SocialAuthView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['provider', 'access_token'],
            properties={
                'provider': openapi.Schema(type=openapi.TYPE_STRING, enum=['google', 'azure']),
                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
            400: "Bad Request"
        },
        operation_description="Authenticate with social provider (Google or Azure)"
    )
    def post(self, request):
        provider = request.data.get('provider')
        access_token = request.data.get('access_token')
        
        if not provider or not access_token:
            return Response({'error': 'Provider and access_token are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if provider not in ['google', 'azure']:
            return Response({'error': 'Provider not supported. Use "google" or "azure"'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle Google OAuth
        if provider == 'google':
            user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
            headers = {'Authorization': f'Bearer {access_token}'}
            try:
                response = requests.get(user_info_url, headers=headers)
                response.raise_for_status()
                user_info = response.json()

                email = user_info.get('userPrincipalName') or user_info.get('mail')
                if not email:
                    return Response({'error': 'Email not provided by Azure'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    user = User.objects.get(email=email)
                    user.azure_id = user_info.get('id')
                    user.social_type = 'azure'
                    user.social_token = access_token
                    user.social_expires_at = timezone.now() + timedelta(hours=1)
                    user.is_email_verified = True
                    user.save()
                except User.DoesNotExist:
                    username = email.split('@')[0]
                    if User.objects.filter(username=username).exists():
                        username = f"{username}{User.objects.count()}"

                    user = User.objects.create_user(
                        email=email,
                        username=username,
                        password=None,
                        first_name=user_info.get('givenName', ''),
                        last_name=user_info.get('surname', ''),
                        azure_id=user_info.get('id'),
                        social_type='azure',
                        social_token=access_token,
                        social_expires_at=timezone.now() + timedelta(hours=1),
                        is_email_verified=True
                    )

                refresh = RefreshToken.for_user(user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            except requests.exceptions.RequestException as e:
                return Response({'error': f'Error validating Azure token: {str(e)}'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Handle Azure OAuth
        elif provider == 'azure':
            # Example endpoint to get user info from Microsoft Graph API
            user_info_url = 'https://graph.microsoft.com/v1.0/me'
            headers = {'Authorization': f'Bearer {access_token}'}

            try:
                response = requests.get(user_info_url, headers=headers)
                response.raise_for_status()
                user_info = response.json()

                email = user_info.get('mail') or user_info.get('userPrincipalName')
                if not email:
                    return Response({'error': 'Email not provided by Azure'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    user = User.objects.get(email=email)
                    user.azure_id = user_info.get('id')
                    user.social_type = 'azure'
                    user.social_token = access_token
                    user.social_expires_at = timezone.now() + timedelta(hours=1)
                    user.is_email_verified = True
                    user.save()
                except User.DoesNotExist:
                    username = email.split('@')[0]
                    if User.objects.filter(username=username).exists():
                        username = f"{username}_{uuid.uuid4().hex[:4]}"

                    user = User.objects.create(
                        username=username,
                        email=email,
                        azure_id=user_info.get('id'),
                        social_type='azure',
                        social_token=access_token,
                        social_expires_at=timezone.now() + timedelta(hours=1),
                        is_email_verified=True
                    )
                    user.set_unusable_password()
                    user.save()

            except requests.RequestException:
                return Response({'error': 'Failed to fetch user info from Azure'}, status=status.HTTP_400_BAD_REQUEST)

            # Return tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })

# Role ViewSet
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    
    @swagger_auto_schema(
        operation_description="List all roles",
        responses={
            200: RoleSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new role",
        request_body=RoleSerializer,
        responses={
            201: RoleSerializer
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve a role by ID",
        responses={
            200: RoleSerializer
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a role",
        request_body=RoleSerializer,
        responses={
            200: RoleSerializer
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a role",
        responses={
            204: "No content"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('role', 'department').order_by('first_name')
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        if user.role and user.role.name == 'Manager' and user.department:
            department = user.department
            department.manager = user
            department.save()

    @swagger_auto_schema(
        operation_description="List all users",
        responses={
            200: UserSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @swagger_auto_schema(
        operation_description="Retrieve a user by ID",
        responses={
            200: UserSerializer
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a user",
        request_body=UserSerializer,
        responses={
            200: UserSerializer
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a user",
        responses={
            204: "No content"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

class ManagerListView(generics.ListAPIView):
    serializer_class = ManagerListSerializer

    def get_queryset(self):
        return User.objects.filter(role__name='Manager')


class UserCountByDepartmentView(APIView):
    def get(self, request):
        data = []
        for dept in Department.objects.all():
            count = dept.user_set.count()
            data.append({
                'department': dept.name,
                'total_employees': count
            })
        return Response(data)

# Event Dashboard
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


# LeaveType ViewSet
class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]

class LeaveSettingView(generics.RetrieveUpdateAPIView):
    serializer_class = LeaveSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, created = LeaveSetting.objects.get_or_create(pk=1)
        return obj

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admins and managers can see all; employees only their own
        if user.is_staff or (user.role and user.role.name == 'Manager'):
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        # Employees can only update their own requests (before approval)
        if instance.user != user and not (user.is_staff or (user.role and user.role.name == 'Manager')):
            raise PermissionDenied("You can only modify your own leave requests.")

        # If employee is editing a request that's already approved/rejected, block it
        if instance.user == user and instance.status in ['Approved', 'Rejected']:
            raise PermissionDenied("You cannot modify a request that has already been processed.")

        serializer.save()


# LeaveSummary ViewSet
class LeaveSummaryViewSet(viewsets.ModelViewSet):
    queryset = LeaveSummary.objects.all()
    serializer_class = LeaveSummarySerializer

# LeaveApproval ViewSet
class LeaveApprovalViewSet(viewsets.ModelViewSet):
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer
