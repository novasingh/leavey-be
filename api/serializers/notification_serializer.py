from rest_framework import serializers
from api.models.notification import Notification

class NotificationSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Notification
        fields = '__all__'
