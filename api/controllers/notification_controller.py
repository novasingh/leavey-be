from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.models import Notification
from api.serializers.notification_serializer import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="User ID to filter notifications", type=openapi.TYPE_INTEGER)
        ],
        operation_description="List notifications. If user_id is provided, filter by user. Otherwise, return all notifications."
    )
    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        queryset = Notification.objects.all().order_by('-created_at')
        if user_id:
            queryset = queryset.filter(users__id=user_id)
        # Group notifications by content and aggregate user IDs
        grouped = {}
        for notif in queryset:
            key = (notif.title, notif.message, notif.notif_type, notif.is_read, notif.created_at)
            if key not in grouped:
                grouped[key] = {
                    'id': notif.id,
                    'title': notif.title,
                    'message': notif.message,
                    'notif_type': notif.notif_type,
                    'is_read': notif.is_read,
                    'created_at': notif.created_at,
                    'users': []
                }
            grouped[key]['users'].extend(list(notif.users.values_list('id', flat=True)))
        return Response(list(grouped.values()))

    @swagger_auto_schema(
        operation_description="Create a new notification. If 'user' is 'all', send to all users. If 'user' is a list, send to selected users. Otherwise, send to one user."
    )
    def create(self, request, *args, **kwargs):
        user_field = request.data.get('user')
        from api.models.user import User
        if user_field == 'all':
            users = User.objects.filter(is_active=True)
        elif isinstance(user_field, list):
            users = User.objects.filter(id__in=user_field)
        else:
            users = User.objects.filter(id=user_field)
        notif = Notification.objects.create(
            title=request.data['title'],
            message=request.data['message'],
            notif_type=request.data['notif_type'],
            is_read=request.data.get('is_read', False)
        )
        notif.users.set(users)
        notif.save()
        return Response(self.get_serializer(notif).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Update a notification by ID."
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a notification by ID."
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='post',
        operation_description="Mark a notification as read for a user. Pass notification_id and user_id in the body.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'notification_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['notification_id', 'user_id']
        )
    )
    @action(detail=False, methods=['post'], url_path='notification_read')
    def notification_read(self, request):
        notification_id = request.data.get('notification_id')
        user_id = request.data.get('user_id')
        if not notification_id or not user_id:
            return Response({'detail': 'notification_id and user_id are required.'}, status=400)
        try:
            notif = Notification.objects.get(id=notification_id, users__id=user_id)
            notif.is_read = True
            notif.save()
            return Response({'detail': 'Notification marked as read.'})
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found for this user.'}, status=404)
