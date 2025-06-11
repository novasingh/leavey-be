# Leavey Project

## Setup Instructions

### Prerequisites
- Python 3.9+ 
- PostgreSQL 12+ ( Install pdAmin `https://www.pgadmin.org/download/pgadmin-4-windows/`)

### Database Setup
1. Install PostgreSQL if not already installed
2. Create a database named `leavey_db`:
   ```sql
   CREATE DATABASE leavey_db;
   ```
3. Make sure the PostgreSQL server is running on port 5432

### Environment Setup
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   **Note**: The requirements.txt file should include Pillow. If you are installing dependencies manually, make sure to install Pillow for image handling:
   ```bash
   pip install Pillow
   ```
5. Copy `.env.example` to `.env` and update the values as needed:
   ```bash
   cp .env.example .env
   ```

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
- `POST /api/auth/password-reset/` - Request password reset
- `POST /api/auth/password-reset/confirm/` - Reset password with token
- `POST /api/auth/social/` - Authenticate with social provider (Google or Azure)
- `POST /api/token/refresh/` - Refresh JWT token

### Users
- `GET /api/users/` - List all users
- `POST /api/users/` - Create a new user
- `GET /api/users/{id}/` - Retrieve a user by ID
- `PUT /api/users/{id}/` - Update a user
- `DELETE /api/users/{id}/` - Delete a user

### Roles
- `GET /api/roles/` - List all roles
- `POST /api/roles/` - Create a new role
- `GET /api/roles/{id}/` - Retrieve a role by ID
- `PUT /api/roles/{id}/` - Update a role
- `DELETE /api/roles/{id}/` - Delete a role
