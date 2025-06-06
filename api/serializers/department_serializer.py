from rest_framework import serializers
from api.models import Department
from api.models.user import User

class DepartmentSerializer(serializers.ModelSerializer):
    total_employees = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at', 'total_employees','manager_name']

    def get_total_employees(self, obj):
        return obj.user_set.count()  # Or obj.users.count() if you used related_name='users'

    def get_manager_name(self, obj):
        # Find the user(s) with role 'Manager' and department = obj.id
        # Assuming role id 2 corresponds to Manager role, adjust if needed
        managers = User.objects.filter(department=obj, role__name='Manager')

        if managers.exists():
            # Return the first manager's full name (or username)
            manager = managers.first()
            return manager.get_full_name() or manager.username
        else:
            return "No manager assigned"
