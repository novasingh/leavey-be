from rest_framework import serializers
from api.models import Event

class EventSerializer(serializers.ModelSerializer):
    day = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = ['day', 'date', 'holiday_name', 'holiday_type']