"""
Database seeding utilities for the Leavey API
"""
from django.db import transaction
from api.models.role import Role
from api.models.department import Department
from api.models.user import User
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)

def seed_database(force=False):
    """
    Seed the database with default roles, departments, and users
    
    Args:
        force (bool): If True, update existing records with new data
        
    Returns:
        dict: Summary of seeding results
    """
    results = {
        'roles_created': 0,
        'departments_created': 0,
        'users_created': 0,
        'success': True,
        'message': ''
    }
    
    try:
        with transaction.atomic():
            # Seed roles
            roles_created = _seed_roles(force)
            results['roles_created'] = roles_created
            
            # Seed departments
            departments_created = _seed_departments(force)
            results['departments_created'] = departments_created
            
            # Seed users
            users_created = _seed_users(force)
            results['users_created'] = users_created
            
            results['message'] = 'Database seeding completed successfully!'
            logger.info('Database seeding completed successfully')
            
    except Exception as e:
        results['success'] = False
        results['message'] = f'Error during seeding: {str(e)}'
        logger.error(f'Database seeding failed: {str(e)}')
    
    return results

def _seed_roles(force=False):
    """Seed default roles"""
    roles_data = [
        {
            'name': 'Admin',
            'description': 'System administrator with full access to all features and settings'
        },
        {
            'name': 'Manager',
            'description': 'Department manager with access to team management and reporting'
        },
        {
            'name': 'HR',
            'description': 'Human Resources personnel with access to employee management'
        },
        {
            'name': 'Employee',
            'description': 'Regular employee with basic access to personal features'
        }
    ]
    
    created_count = 0
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={
                'description': role_data['description'],
                'is_active': True
            }
        )
        
        if created:
            created_count += 1
            logger.info(f'Created role: {role.name}')
        elif force:
            role.description = role_data['description']
            role.save()
            logger.info(f'Updated role: {role.name}')
    
    return created_count

def _seed_departments(force=False):
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
    
    created_count = 0
    for dept_data in departments_data:
        department, created = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={
                'description': dept_data['description'],
                'is_active': True
            }
        )
        
        if created:
            created_count += 1
            logger.info(f'Created department: {department.name}')
        elif force:
            department.description = dept_data['description']
            department.save()
            logger.info(f'Updated department: {department.name}')
    
    return created_count

def _seed_users(force=False):
    """Seed default users"""
    # Get roles and departments
    try:
        admin_role = Role.objects.get(name='Admin')
        manager_role = Role.objects.get(name='Manager')
        hr_role = Role.objects.get(name='HR')
        employee_role = Role.objects.get(name='Employee')
        
        admin_dept = Department.objects.get(name='Administration')
        hr_dept = Department.objects.get(name='Human Resources')
        it_dept = Department.objects.get(name='IT')
        finance_dept = Department.objects.get(name='Finance')
    except (Role.DoesNotExist, Department.DoesNotExist) as e:
        logger.error(f'Required roles or departments not found: {str(e)}')
        raise
    
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
    
    created_count = 0
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
            created_count += 1
            logger.info(f'Created user: {user.email} ({user.role.name})')
        elif force:
            # Update user data except password
            for key, value in user_data.items():
                setattr(user, key, value)
            user.save()
            logger.info(f'Updated user: {user.email}')

    # Set manager relationships
    _set_manager_relationships()
    
    return created_count

def _set_manager_relationships():
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

        it_department = Department.objects.get(name='IT')
        it_department.manager = manager_user
        it_department.save()

        logger.info('Manager relationships and department manager set successfully')


    except (User.DoesNotExist, Department.DoesNotExist) as e:
        logger.warning(f'Could not set manager relationships or department manager: {str(e)}')

def check_seed_status():
    """
    Check if the database has been seeded with default data
    
    Returns:
        dict: Status information about seeded data
    """
    status = {
        'roles_count': Role.objects.count(),
        'departments_count': Department.objects.count(),
        'users_count': User.objects.count(),
        'has_admin': User.objects.filter(email='admin@leavey.com').exists(),
        'is_seeded': False
    }
    
    # Consider database seeded if we have the basic roles and admin user
    status['is_seeded'] = (
        status['roles_count'] >= 4 and 
        status['departments_count'] >= 5 and 
        status['has_admin']
    )
    
    return status
