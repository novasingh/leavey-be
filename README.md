# University of Malaya Group Project

**Students:**
- Abdi Ahmed Mohamed (2190992)
- Akashdeep Singh (24072095)
- Najla Geis Junaid Bawazier (24068527)
- Salsabila Harlen (24076059)
- Zahra Fathanah (23067637)

# Leavey Project

## Project Overview
A robust Django REST API for leave management, notifications, and HR workflows. Features include PostgreSQL integration, Swagger docs, CORS, comprehensive seeding, in-app/email notifications, and modular structure for easy extension.

## Project Structure
```
leavey-be-main/
├── api/
│   ├── __init__.py
│   ├── admin.py
│   ├── controllers/
│   │   ├── notification_controller.py
│   │   ├── permission_controller.py
│   │   ├── seed_controller.py
│   │   └── ...
│   ├── email_templates/
│   │   ├── leave_status.html
│   │   ├── leave_submitted.html
│   │   ├── notification.html
│   │   └── reset_password.html
│   ├── management/
│   │   └── commands/
│   │       ├── seed_data.py
│   │       └── check_seed.py
│   ├── migrations/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── department.py
│   │   ├── event.py
│   │   ├── leave.py
│   │   ├── notification.py
│   │   ├── notification_setting.py
│   │   ├── role.py
│   │   └── user.py
│   ├── serializers/
│   │   ├── notification_serializer.py
│   │   └── ...
│   ├── utils/
│   │   ├── emails.py
│   │   ├── notifications.py
│   │   ├── seeder.py
│   │   └── ...
│   └── views.py
├── leavey_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
├── .env
├── .gitignore
├── manage.py
├── README.md
├── SEEDING.md
```

## Key Modules & Features
- **User, Role, Department, Leave, Notification, Event, NotificationSetting** models
- **Controllers** for modular API logic
- **Comprehensive seeding** for roles, departments, users, leave types, holidays, and dummy data
- **Notification system**: in-app & email, with templates for leave submission/status and password reset
- **Swagger/OpenAPI** docs at `/swagger/`
- **CORS** and environment variable support
- **Admin panel** for all models
- **Robust .env-driven configuration**
- **Permission listing** endpoint for all unique permissions
- **Grouped notification listing and mark-as-read**

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 12+

### Database Setup
1. Install PostgreSQL
2. Create a database named `leavey_db`:
   ```sql
   CREATE DATABASE leavey_db;
   ```
3. Ensure PostgreSQL is running on the port set in `.env`

### Environment Setup
1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Unix/MacOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and update values as needed

### Running Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating a Superuser
```bash
python manage.py createsuperuser
```

### Running the Development Server
```bash
python manage.py runserver
```

### API Documentation
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login with email and password
- `GET /api/auth/verify-email/` - Verify email with token
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/password-reset/confirm/` - Reset password with token
- `POST /api/auth/social/` - Authenticate with social provider (Google or Azure)

### Users
- `GET /api/users/` - List all users
- `POST /api/users/` - Create a new user
- `GET /api/users/{id}/` - Retrieve a user by ID
- `PUT /api/users/{id}/` - Update a user
- `DELETE /api/users/{id}/` - Delete a user
- `GET /api/profile/` - Get current user's profile

### Roles
- `GET /api/roles/` - List all roles
- `POST /api/roles/` - Create a new role
- `GET /api/roles/{id}/` - Retrieve a role by ID
- `PUT /api/roles/{id}/` - Update a role
- `DELETE /api/roles/{id}/` - Delete a role

### Departments
- `GET /api/departments/` - List all departments
- `POST /api/departments/` - Create a new department
- `GET /api/departments/{id}/` - Retrieve a department by ID
- `PUT /api/departments/{id}/` - Update a department
- `DELETE /api/departments/{id}/` - Delete a department
- `GET /api/departments/user-count` - Get user count by department
- `GET /api/managers/` - List all managers

### Leave Types & Requests
- `GET /api/leave-types/` - List all leave types
- `POST /api/leave-types/` - Create a leave type
- `GET /api/leave-types/{id}/` - Retrieve a leave type
- `PUT /api/leave-types/{id}/` - Update a leave type
- `DELETE /api/leave-types/{id}/` - Delete a leave type
- `GET /api/leave-requests/` - List all leave requests
- `POST /api/leave-requests/` - Create a leave request
- `GET /api/leave-requests/{id}/` - Retrieve a leave request
- `PUT /api/leave-requests/{id}/` - Update a leave request
- `DELETE /api/leave-requests/{id}/` - Delete a leave request
- `GET /api/leave-settings/` - Get leave settings

### Events
- `GET /api/events/` - List all events
- `POST /api/events/` - Create an event
- `GET /api/events/{id}/` - Retrieve an event
- `PUT /api/events/{id}/` - Update an event
- `DELETE /api/events/{id}/` - Delete an event

### Notifications
- `GET /api/notifications/` - List all notifications (grouped by user)
- `POST /api/notifications/` - Send a notification (to all, selected, or single users)
- `GET /api/notifications/{id}/` - Retrieve a notification
- `PUT /api/notifications/{id}/` - Update a notification
- `DELETE /api/notifications/{id}/` - Delete a notification
- `POST /api/notifications/{id}/mark-as-read/` - Mark notification as read

### Seeding
- `GET /api/seed/status/` - Public seeding status
- `POST /api/admin/seed/` - Seed database (admin only)
- `GET /api/admin/seed/` - Detailed seeding status (admin only)

### Permissions
- `GET /api/permission-all/` - List all unique permissions (plus 'notification')

### CORS Test
- `GET /api/test/cors/` - Test CORS GET
- `POST /api/test/cors/post/` - Test CORS POST

---

## Credits
This project is a group effort by University of Malaya students for academic purposes.
