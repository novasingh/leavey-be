from django.core.management.base import BaseCommand
from django.db import transaction
from api.models.role import Role
from api.models.department import Department
from api.models.user import User
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seed the database with default roles, departments, and users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force seed even if data already exists',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        try:
            with transaction.atomic():
                # Seed roles
                self.seed_roles(force)
                
                # Seed departments
                self.seed_departments(force)
                
                # Seed leave types
                self.seed_leave_types(force)
                
                # Seed leave settings
                self.seed_leave_settings(force)
                
                # Seed public holidays
                self.seed_public_holidays(force)
                
                # Seed users
                self.seed_users(force)
                
            self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during seeding: {str(e)}'))
            logger.error(f'Database seeding failed: {str(e)}')

    def seed_roles(self, force=False):
        """Seed default roles with permissions"""
        roles_data = [
            {
                'name': 'Admin',
                'description': 'System administrator with full access to all features and settings',
                'permissions': [
                    'dashboard', 'department', 'role', 'leave-setting', 'employees'
                ]
            },
            {
                'name': 'Manager',
                'description': 'Department manager with access to team management and reporting',
                'permissions': [
                    'dashboard', 'leaves-approval', 'leave-history'
                ]
            },
            {
                'name': 'HR',
                'description': 'Human Resources personnel with access to employee management',
                'permissions': [
                    'dashboard', 'department', 'role', 'leave-setting', 'employees'
                ]
            },
            {
                'name': 'Employee',
                'description': 'Regular employee with basic access to personal features',
                'permissions': [
                    'dashboard', 'my-leaves', 'calender', 'faq'
                ]
            }
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'is_active': True,
                    'permissions': role_data['permissions']
                }
            )
            if created:
                self.stdout.write(f'Created role: {role.name}')
            elif force:
                role.description = role_data['description']
                role.permissions = role_data['permissions']
                role.save()
                self.stdout.write(f'Updated role: {role.name}')
            else:
                self.stdout.write(f'Role already exists: {role.name}')

    def seed_departments(self, force=False):
        """Seed default departments"""
        departments_data = [
            {
                'name': 'Administration',
                'description': 'Administrative and management department'
            },
            {
                'name': 'Human Resources',
                'description': 'Human resources and employee relations'
            },
            {
                'name': 'IT',
                'description': 'Information Technology department'
            },
            {
                'name': 'Finance',
                'description': 'Finance and accounting department'
            },
            {
                'name': 'Operations',
                'description': 'Operations and business processes'
            }
        ]
        
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={
                    'description': dept_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created department: {department.name}')
            elif force:
                department.description = dept_data['description']
                department.save()
                self.stdout.write(f'Updated department: {department.name}')
            else:
                self.stdout.write(f'Department already exists: {department.name}')

    def seed_leave_types(self, force=False):
        """Seed default leave types"""
        leave_types_data = [
            {
                'name': 'Annual Leave',
                'description': 'Paid time off for vacation or personal use',
                'days': 20,
                'is_active': True,
                'color': '#4CAF50',
            },
            {
                'name': 'Sick Leave',
                'description': 'Paid time off for illness or medical needs',
                'days': 10,
                'is_active': True,
                'color': '#F44336',
            },
            {
                'name': 'Casual Leave',
                'description': 'Short-term leave for personal matters',
                'days': 7,
                'is_active': True,
                'color': '#2196F3',
            },
            {
                'name': 'Maternity Leave',
                'description': 'Leave for maternity purposes',
                'days': 90,
                'is_active': True,
                'color': '#E91E63',
            },
            {
                'name': 'Paternity Leave',
                'description': 'Leave for paternity purposes',
                'days': 15,
                'is_active': True,
                'color': '#9C27B0',
            },
        ]
        from api.models.leave import LeaveType
        for leave_type_data in leave_types_data:
            leave_type, created = LeaveType.objects.get_or_create(
                name=leave_type_data['name'],
                defaults=leave_type_data
            )
            if created:
                self.stdout.write(f'Created leave type: {leave_type.name}')
            elif force:
                for key, value in leave_type_data.items():
                    setattr(leave_type, key, value)
                leave_type.save()
                self.stdout.write(f'Updated leave type: {leave_type.name}')
            else:
                self.stdout.write(f'Leave type already exists: {leave_type.name}')

    def seed_leave_settings(self, force=False):
        """Seed default leave settings (singleton)"""
        from api.models.leave import LeaveSetting
        defaults = {
            'working_hours_start': '09:00',
            'working_hours_end': '17:00',
            'is_flexible_hours_enabled': False,
            'is_weekday_workday': True,
            'is_weekend_workday': False,
            'cycle_type': 'annual',
        }
        leave_setting, created = LeaveSetting.objects.get_or_create(
            singleton_id=1,
            defaults=defaults
        )
        if created:
            self.stdout.write('Created default leave settings')
        elif force:
            for key, value in defaults.items():
                setattr(leave_setting, key, value)
            leave_setting.save()
            self.stdout.write('Updated default leave settings')
        else:
            self.stdout.write('Leave settings already exist')

    def seed_public_holidays(self, force=False):
        """Seed default public holidays for Malaysia using the Event model fields"""
        from api.models.event import Event
        from datetime import datetime
        holidays_data = [
            {
                'holiday_name': "New Year's Day",
                'date': '2025-01-01',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Federal Territory Day",
                'date': '2025-02-01',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Chinese New Year",
                'date': '2025-01-29',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Chinese New Year (2nd day)",
                'date': '2025-01-30',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Labour Day",
                'date': '2025-05-01',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Wesak Day",
                'date': '2025-05-12',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Hari Raya Aidilfitri",
                'date': '2025-03-30',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Hari Raya Aidilfitri (2nd day)",
                'date': '2025-03-31',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Agong's Birthday",
                'date': '2025-06-02',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Hari Raya Haji",
                'date': '2025-06-07',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Awal Muharram",
                'date': '2025-07-27',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Merdeka Day",
                'date': '2025-08-31',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Malaysia Day",
                'date': '2025-09-16',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Prophet Muhammad's Birthday",
                'date': '2025-09-15',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Deepavali",
                'date': '2025-10-20',
                'holiday_type': 'Public Holiday',
            },
            {
                'holiday_name': "Christmas Day",
                'date': '2025-12-25',
                'holiday_type': 'Public Holiday',
            },
        ]
        for holiday in holidays_data:
            date_obj = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            event, created = Event.objects.get_or_create(
                holiday_name=holiday['holiday_name'],
                date=date_obj,
                defaults={
                    'holiday_type': holiday['holiday_type']
                }
            )
            if created:
                self.stdout.write(f"Created public holiday: {event.holiday_name}")
            elif force:
                event.holiday_type = holiday['holiday_type']
                event.save()
                self.stdout.write(f"Updated public holiday: {event.holiday_name}")
            else:
                self.stdout.write(f"Public holiday already exists: {event.holiday_name}")

    def seed_users(self, force=False):
        """Seed default users"""
        # Get roles and departments
        admin_role = Role.objects.get(name='Admin')
        manager_role = Role.objects.get(name='Manager')
        hr_role = Role.objects.get(name='HR')
        employee_role = Role.objects.get(name='Employee')
        
        admin_dept = Department.objects.get(name='Administration')
        hr_dept = Department.objects.get(name='Human Resources')
        it_dept = Department.objects.get(name='IT')
        finance_dept = Department.objects.get(name='Finance')
        
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@leavey.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': admin_role,
                'department': admin_dept,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'is_email_verified': True,
                'password': 'admin123'  # Change this in production
            },
            {
                'username': 'manager',
                'email': 'manager@leavey.com',
                'first_name': 'Department',
                'last_name': 'Manager',
                'role': manager_role,
                'department': it_dept,
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
                'is_email_verified': True,
                'password': 'manager123'
            },
            {
                'username': 'hr',
                'email': 'hr@leavey.com',
                'first_name': 'Human',
                'last_name': 'Resources',
                'role': hr_role,
                'department': hr_dept,
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
                'is_email_verified': True,
                'password': 'hr123'
            },
            {
                'username': 'employee',
                'email': 'employee@leavey.com',
                'first_name': 'Test',
                'last_name': 'Employee',
                'role': employee_role,
                'department': finance_dept,
                'is_staff': False,
                'is_superuser': False,
                'is_active': True,
                'is_email_verified': True,
                'password': 'employee123'
            }
        ]
        
        for user_data in users_data:
            password = user_data.pop('password')
            
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    **user_data,
                    'password': make_password(password)
                }
            )
            
            if created:
                self.stdout.write(f'Created user: {user.email} ({user.role.name})')
                self.stdout.write(f'  Username: {user.username}')
                self.stdout.write(f'  Password: {password}')
                self.stdout.write('  ---')
            elif force:
                # Update user data except password
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.save()
                self.stdout.write(f'Updated user: {user.email}')
            else:
                self.stdout.write(f'User already exists: {user.email}')

        # Set manager relationships
        self.set_manager_relationships()

    def set_manager_relationships(self):
        """Set up manager relationships between users"""
        try:
            admin_user = User.objects.get(email='admin@leavey.com')
            manager_user = User.objects.get(email='manager@leavey.com')
            hr_user = User.objects.get(email='hr@leavey.com')
            employee_user = User.objects.get(email='employee@leavey.com')
            
            # Set manager relationships
            manager_user.manager = admin_user
            hr_user.manager = admin_user
            employee_user.manager = manager_user
            
            manager_user.save()
            hr_user.save()
            employee_user.save()
            
            self.stdout.write('Manager relationships set successfully')
            
        except User.DoesNotExist as e:
            self.stdout.write(self.style.WARNING(f'Could not set manager relationships: {str(e)}'))
