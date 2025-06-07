from rest_framework import serializers
from api.models import Department, User

class DepartmentSerializer(serializers.ModelSerializer):
    # manager = serializers.StringRelatedField()

    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True, default='No manager assigned')
    total_employees = serializers.SerializerMethodField()
    # manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        # fields = '__all__'
        fields = ['id', 'name','description', 'is_active', 'manager', 'manager_name', 'total_employees']
        extra_kwargs = {
            # This makes 'manager' a write-only field that expects an ID.
            'manager': {'write_only': True, 'required': False, 'allow_null': True}
        }

    # def get_manager_name(self, obj):
    #     # Find the user(s) with role 'Manager' and department = obj.id
    #     managers = User.objects.filter(department=obj, role__name='Manager')
    #
    #     if managers.exists():
    #     # Return the first manager's full name (or username)
    #         manager = managers.first()
    #         return manager.get_full_name() or manager.username
    #     else:
    #         return "No manager assigned"

    def get_total_employees(self, obj):
        return obj.user_set.count()  # Or obj.users.count() if you used related_name='users'

        # def validate_manager(self, value):
        #     if value and value.role and value.role.name.lower() != "manager":
        #         raise serializers.ValidationError("Selected user is not assigned the manager role.")
        #     return value