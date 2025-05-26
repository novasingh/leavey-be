from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from api.models.role import Role

@api_view(['GET'])
@permission_classes([AllowAny])
def permission_all(request):
    """
    Get all unique permissions available in the system (from all roles)
    """
    all_permissions = set()
    for role in Role.objects.all():
        if isinstance(role.permissions, list):
            all_permissions.update(role.permissions)
    return Response({
        'permissions': sorted(list(all_permissions))
    })
