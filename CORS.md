# CORS Configuration for Leavey API

This document explains the CORS (Cross-Origin Resource Sharing) configuration for the Leavey API.

## What is CORS?

CORS is a security feature implemented by web browsers to prevent websites from making requests to different domains unless explicitly allowed. Since your frontend (React, Vue, Angular, etc.) will likely run on a different port or domain than your Django API, you need to configure CORS to allow these cross-origin requests.

## Current Configuration

### Development Mode
In development (`DEBUG=True`), the API allows requests from all origins for easier testing:
- `CORS_ALLOW_ALL_ORIGINS = True`

### Production Mode
In production (`DEBUG=False`), only specific origins are allowed:
- `http://localhost:3000` (React default)
- `http://localhost:8080` (Vue default)
- `http://localhost:4200` (Angular default)
- Add your production frontend domain

## Environment Variables

You can customize CORS settings using environment variables in your `.env` file:

```bash
# Allow all origins in development (True/False)
CORS_ALLOW_ALL_ORIGINS=True

# Comma-separated list of allowed origins for production
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourfrontend.com

# Allow credentials in CORS requests (True/False)
CORS_ALLOW_CREDENTIALS=True
```

## Frontend Integration Examples

### React/Next.js
```javascript
// API call example
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include', // Important for CORS with credentials
  body: JSON.stringify({
    email: 'admin@leavey.com',
    password: 'admin123'
  })
});
```

### Axios Configuration
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // Important for CORS with credentials
  headers: {
    'Content-Type': 'application/json',
  }
});

// Usage
const login = async (credentials) => {
  const response = await api.post('/auth/login/', credentials);
  return response.data;
};
```

### Vue.js
```javascript
// In your Vue component or service
async login(credentials) {
  try {
    const response = await this.$http.post('/auth/login/', credentials, {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
  }
}
```

## Troubleshooting CORS Issues

### Common Error Messages

1. **"Access to fetch at '...' from origin '...' has been blocked by CORS policy"**
   - Add your frontend URL to `CORS_ALLOWED_ORIGINS`
   - Ensure `corsheaders` is installed and configured

2. **"Preflight request doesn't pass access control check"**
   - Make sure `corsheaders.middleware.CorsMiddleware` is first in `MIDDLEWARE`
   - Check that the HTTP method is in `CORS_ALLOWED_METHODS`

3. **"Credentials flag is 'true', but the Access-Control-Allow-Credentials header is 'false'"**
   - Set `CORS_ALLOW_CREDENTIALS = True`
   - Cannot use `CORS_ALLOW_ALL_ORIGINS = True` with credentials

### Debug Steps

1. Check browser developer tools Network tab for CORS errors
2. Verify the OPTIONS preflight request is successful
3. Ensure your frontend URL is in the allowed origins list
4. Check that required headers are in `CORS_ALLOW_HEADERS`

## Security Best Practices

### For Production

1. **Never use `CORS_ALLOW_ALL_ORIGINS = True` in production**
2. **Specify exact domains** in `CORS_ALLOWED_ORIGINS`
3. **Use HTTPS** for production domains
4. **Limit exposed headers** to what's actually needed

Example production configuration:
```python
CORS_ALLOWED_ORIGINS = [
    "https://yourapp.com",
    "https://www.yourapp.com",
    "https://app.yourcompany.com",
]
CORS_ALLOW_CREDENTIALS = True
```

### For Development

1. Use `CORS_ALLOW_ALL_ORIGINS = True` for convenience
2. Test with specific origins before production deployment
3. Use localhost and 127.0.0.1 variants for local testing

## Adding New Frontend Domains

To add a new frontend domain:

1. **For development**: No changes needed if `CORS_ALLOW_ALL_ORIGINS = True`
2. **For production**: Add the domain to `CORS_ALLOWED_ORIGINS` list

Example:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://staging.yourapp.com",  # Add staging environment
    "https://yourapp.com",          # Add production domain
]
```

## Testing CORS Configuration

### Using curl
```bash
# Test a simple GET request
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/api/auth/login/
```

### Using Browser Console
```javascript
// Test from browser console
fetch('http://localhost:8000/api/seed/status/', {
  method: 'GET',
  mode: 'cors',
  credentials: 'include'
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('CORS Error:', error));
```

## Advanced Configuration

### Custom Headers
If your frontend needs to send custom headers:
```python
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-custom-header',  # Add your custom header
]
```

### Multiple Subdomains
To allow all subdomains of a domain:
```python
# Note: This requires more advanced configuration
# For now, add each subdomain explicitly
CORS_ALLOWED_ORIGINS = [
    "https://app.yourcompany.com",
    "https://admin.yourcompany.com",
    "https://api.yourcompany.com",
]
```
