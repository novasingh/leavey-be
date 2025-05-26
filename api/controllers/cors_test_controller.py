from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings

@swagger_auto_schema(
    method='get',
    operation_description="Test CORS configuration and API connectivity",
    responses={
        200: openapi.Response(
            description="CORS test successful",
            examples={
                "application/json": {
                    "message": "CORS is working!",
                    "cors_settings": {
                        "allow_all_origins": True,
                        "allow_credentials": True,
                        "allowed_origins": ["http://localhost:3000"]
                    },
                    "timestamp": "2025-01-26T10:30:00Z"
                }
            }
        )
    }
)
@api_view(['GET', 'OPTIONS'])
@permission_classes([AllowAny])
def cors_test(request):
    """
    Test endpoint to verify CORS configuration
    No authentication required
    """
    from datetime import datetime
    
    cors_info = {
        'message': 'CORS is working!',
        'cors_settings': {
            'allow_all_origins': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
            'allow_credentials': getattr(settings, 'CORS_ALLOW_CREDENTIALS', False),
            'allowed_origins': getattr(settings, 'CORS_ALLOWED_ORIGINS', []),
            'allowed_methods': getattr(settings, 'CORS_ALLOWED_METHODS', []),
        },
        'request_info': {
            'method': request.method,
            'origin': request.META.get('HTTP_ORIGIN', 'Not provided'),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Not provided'),
        },
        'timestamp': datetime.now().isoformat(),
        'debug_mode': settings.DEBUG,
    }
    
    return Response(cors_info, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Test CORS with POST request",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'test_data': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Test data to echo back',
                default='Hello from frontend!'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="POST request successful",
            examples={
                "application/json": {
                    "message": "POST request received",
                    "echo": "Hello from frontend!",
                    "timestamp": "2025-01-26T10:30:00Z"
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def cors_test_post(request):
    """
    Test endpoint for POST requests with CORS
    No authentication required
    """
    from datetime import datetime
    
    response_data = {
        'message': 'POST request received successfully!',
        'echo': request.data.get('test_data', 'No test data provided'),
        'content_type': request.content_type,
        'timestamp': datetime.now().isoformat(),
    }
    
    return Response(response_data, status=status.HTTP_200_OK)
