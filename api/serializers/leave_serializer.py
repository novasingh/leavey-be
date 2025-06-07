from rest_framework import serializers
from api.models.leave import LeaveType, LeaveRequest, LeaveSummary, LeaveApproval


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'
        read_only_fields = ['leave_type_id']


# class LeaveRequestSerializer(serializers.ModelSerializer):
#     leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all())
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
#     class Meta:
#         model = LeaveRequest
#         fields = '__all__'
#         read_only_fields = ['request_id', 'created_at', 'updated_at', 'days', 'user']



class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)


    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = [
            'request_id',
            'created_at',
            'updated_at',
            'days',
            'user',
        ]

    def update(self, instance, validated_data):
        """
        Allow updating status and rejection_reason only if user is a manager or admin.
        """
        user = self.context['request'].user

        # Employees can only update their own request and cannot update status
        if instance.user == user:
            validated_data.pop('status', None)
            validated_data.pop('note', None)
        
        # Managers/admins can update status/reason
        elif user.is_staff or (user.role and user.role.name == 'Manager'):
            # Optional logic: prevent changing to invalid status
            allowed_statuses = ['Pending', 'Approved', 'Rejected', 'Cancelled']
            if 'status' in validated_data and validated_data['status'] not in allowed_statuses:
                raise serializers.ValidationError({'status': 'Invalid status.'})
        else:
            raise serializers.ValidationError("You do not have permission to update this request.")

        return super().update(instance, validated_data)

class LeaveSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveSummary
        fields = '__all__'
        read_only_fields = ['summary_id', 'created_at', 'updated_at', 'days_taken', 'status', 'reviewed_by', 'note']

class LeaveApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApproval
        fields = '__all__'
        read_only_fields = ['approval_id', 'created_at', 'updated_at']
