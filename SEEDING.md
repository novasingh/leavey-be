# Database Seeding for Leavey API

This document explains how to seed your database with default and dummy data, including roles, departments, users, leave types, holidays, leave requests, approvals, and more.

## Default Data Created

### Roles
- **Admin**: System administrator with full access
- **Manager**: Department manager with team management access
- **HR**: Human Resources personnel with employee management access
- **Employee**: Regular employee with basic access

### Departments
- **Administration**: Administrative and management department
- **Human Resources**: Human resources and employee relations
- **IT**: Information Technology department
- **Finance**: Finance and accounting department
- **Operations**: Operations and business processes

### Default Users
| Role     | Email               | Username | Password    | Department        |
|----------|---------------------|----------|-------------|-------------------|
| Admin    | admin@leavey.com    | admin    | admin123    | Administration    |
| Manager  | manager@leavey.com  | manager  | manager123  | IT                |
| HR       | hr@leavey.com       | hr       | hr123       | Human Resources   |
| Employee | employee@leavey.com | employee | employee123 | Finance           |

**⚠️ IMPORTANT: Change these default passwords in production!**

### Dummy Data
- 50+ dummy users (randomized)
- Leave types, leave settings, public holidays (Malaysia)
- Leave requests and approvals
- Notification settings and sample notifications

## How to Seed the Database

### Method 1: Management Commands (Recommended)

#### Seed the database manually:
```bash
python manage.py seed_data
```

#### Force update existing data:
```bash
python manage.py seed_data --force
```

#### Check seeding status:
```bash
python manage.py check_seed
```

#### Check status and seed if empty:
```bash
python manage.py check_seed --seed-if-empty
```

### Method 2: Automatic Seeding on Startup

Set the environment variable to enable automatic seeding when the app starts:

```bash
# Windows
set AUTO_SEED=True
# Linux/Mac
export AUTO_SEED=True
# Or add to your .env file
AUTO_SEED=True
```

Then start your Django application:
```bash
python manage.py runserver
```

The database will be automatically seeded if no users exist.

### Method 3: API Endpoints

#### Check seeding status (Public):
```
GET /api/seed/status/
```

Response:
```json
{
    "seeding_needed": false,
    "has_admin": true,
    "message": "Database is properly seeded"
}
```

#### Seed database via API (Admin only):
```
POST /api/admin/seed/
Content-Type: application/json

{
    "force": false
}
```

#### Check detailed seeding status (Admin only):
```
GET /api/admin/seed/
```

Response:
```json
{
    "roles_count": 4,
    "departments_count": 5,
    "users_count": 54,
    "has_admin": true,
    "is_seeded": true
}
```

### Method 4: Programmatic Usage

You can also use the seeding utilities in your Python code:

```python
from api.utils.seeder import seed_database, check_seed_status

# Check if seeding is needed
status = check_seed_status()
if not status['is_seeded']:
    # Seed the database
    result = seed_database()
    if result['success']:
        print("Database seeded successfully!")
    else:
        print(f"Seeding failed: {result['message']}")
```

## Migration and Seeding Workflow

1. **First time setup:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_data
   ```

2. **For development with auto-seeding:**
   ```bash
   # Set environment variable
   export AUTO_SEED=True
   
   # Run migrations
   python manage.py migrate
   
   # Start server (will auto-seed if needed)
   python manage.py runserver
   ```

3. **Production deployment:**
   ```bash
   python manage.py migrate
   python manage.py check_seed --seed-if-empty
   # Change default passwords!
   ```

## Security Notes

- **Always change default passwords in production environments**
- The auto-seeding feature only runs when no users exist in the database
- Auto-seeding is disabled during migrations to prevent conflicts
- Admin endpoints require proper authentication
- Use environment variables to control seeding behavior

## Troubleshooting

### Seeding fails with "Role does not exist"
Make sure migrations are run before seeding:
```bash
python manage.py migrate
python manage.py seed_data
```

### Auto-seeding doesn't work
Check that:
1. `AUTO_SEED=True` is set in environment
2. Database is empty (no users exist)
3. Not running during migrations
4. Tables are created (run migrations first)

### API endpoints return 404
Make sure you've updated your `urls.py` to include the seeding endpoints.

## Customization

To customize the default data, edit the files:
- `api/management/commands/seed_data.py` - Management command
- `api/utils/seeder.py` - Core seeding logic

You can modify:
- Default user credentials
- Role names and descriptions
- Department names and descriptions
- User-manager relationships
- Dummy data generation logic
- Leave types, holidays, and notification templates
