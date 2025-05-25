from django.core.management.base import BaseCommand
from api.utils.seeder import check_seed_status, seed_database

class Command(BaseCommand):
    help = 'Check the status of database seeding'

    def add_arguments(self, parser):
        parser.add_argument(
            '--seed-if-empty',
            action='store_true',
            help='Automatically seed if database is empty',
        )

    def handle(self, *args, **options):
        status = check_seed_status()
        
        self.stdout.write(self.style.SUCCESS('Database Seeding Status:'))
        self.stdout.write(f'  Roles: {status["roles_count"]}')
        self.stdout.write(f'  Departments: {status["departments_count"]}')
        self.stdout.write(f'  Users: {status["users_count"]}')
        self.stdout.write(f'  Has Admin: {"Yes" if status["has_admin"] else "No"}')
        self.stdout.write(f'  Is Seeded: {"Yes" if status["is_seeded"] else "No"}')
        
        if options['seed_if_empty'] and not status['is_seeded']:
            self.stdout.write(self.style.WARNING('Database appears empty, seeding...'))
            result = seed_database()
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS('Seeding completed!'))
                self.stdout.write(f'  Created {result["roles_created"]} roles')
                self.stdout.write(f'  Created {result["departments_created"]} departments')
                self.stdout.write(f'  Created {result["users_created"]} users')
            else:
                self.stdout.write(self.style.ERROR(f'Seeding failed: {result["message"]}'))
