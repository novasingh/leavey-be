from rest_framework import serializers
from api.models.leave import LeaveType, LeaveRequest, LeaveSetting


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'
        read_only_fields = ['leave_type_id']

class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all())
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    # Keep user write-hidden but expose read-only name/email for display
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = [
            'request_id',
            'created_at',
            'updated_at',
            'days',
            'user',  # keep user hidden on creation/update
        ]

    def get_employee_name(self, obj):
        if obj.user:
            full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
            return full_name if full_name else obj.user.username
        return "Unknown"


class LeaveSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveSetting
        fields = '__all__'