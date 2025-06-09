from rest_framework import serializers
from api.models import Department, User

class DepartmentSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True, default='No manager assigned')
    total_employees = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name','icon','description', 'is_active', 'manager', 'manager_name', 'total_employees']
        extra_kwargs = {
            'manager': {'write_only': True, 'required': False, 'allow_null': True}
        }

    def get_total_employees(self, obj):
        return obj.user_set.count()
