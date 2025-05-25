from django.apps import AppConfig
from django.core.management import call_command
import os
import sys


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        """
        This method is called when Django starts.
        We'll seed data only if AUTO_SEED environment variable is set to True
        """
        # Only run seeding in specific conditions to avoid issues during migrations
        if (os.environ.get('AUTO_SEED', 'False').lower() == 'true' and 
            'migrate' not in sys.argv and 
            'makemigrations' not in sys.argv and
            'collectstatic' not in sys.argv):
            
            try:
                # Import here to avoid Django setup issues
                from django.db import connection
                
                # Check if tables exist before seeding
                table_names = connection.introspection.table_names()
                required_tables = ['api_role', 'api_department', 'api_user']
                
                if all(table in table_names for table in required_tables):
                    from .models.user import User
                    
                    # Only seed if no users exist
                    if not User.objects.exists():
                        call_command('seed_data')
                        print("✅ Database seeded with default data")
                    else:
                        print("ℹ️  Database already contains users, skipping seeding")
                        
            except Exception as e:
                print(f"⚠️  Could not auto-seed database: {str(e)}")
