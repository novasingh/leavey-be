from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from api.utils.seeder import seed_database, check_seed_status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="Check the status of database seeding",
    responses={
        200: openapi.Response(
            description="Seeding status",
            examples={
                "application/json": {
                    "roles_count": 4,
                    "departments_count": 5,
                    "users_count": 4,
                    "has_admin": True,
                    "is_seeded": True
                }
            }
        )
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Seed the database with default data (Admin only)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'force': openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description='Force seed even if data already exists',
                default=False
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Seeding completed successfully",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Database seeding completed successfully!",
                    "roles_created": 4,
                    "departments_created": 5,
                    "users_created": 4
                }
            }
        ),
        400: openapi.Response(
            description="Seeding failed",
            examples={
                "application/json": {
                    "success": False,
                    "message": "Error during seeding: ..."
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def seed_database_view(request):
    """
    GET: Check seeding status
    POST: Seed the database with default data (Admin only)
    """
    if request.method == 'GET':
        status_data = check_seed_status()
        return Response(status_data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        force = request.data.get('force', False)
        result = seed_database(force=force)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


# Public endpoint to check if seeding is needed (no auth required)
@swagger_auto_schema(
    method='get',
    operation_description="Check if database seeding is needed (public endpoint)",
    responses={
        200: openapi.Response(
            description="Seeding requirement status",
            examples={
                "application/json": {
                    "seeding_needed": False,
                    "has_admin": True,
                    "message": "Database is properly seeded"
                }
            }
        )
    }
)
@api_view(['GET'])
def seed_status_public(request):
    """
    Public endpoint to check if seeding is needed
    """
    status_data = check_seed_status()
    
    response_data = {
        'seeding_needed': not status_data['is_seeded'],
        'has_admin': status_data['has_admin'],
        'message': 'Database seeding needed' if not status_data['is_seeded'] else 'Database is properly seeded'
    }
    
    return Response(response_data, status=status.HTTP_200_OK)
