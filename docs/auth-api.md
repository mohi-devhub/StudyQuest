# Authentication API Reference

## Endpoints

### POST /auth/signup
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2025-11-05T..."
  }
}
```

**Errors:**
- 409 Conflict: Email already registered
- 400 Bad Request: Invalid input

---

### POST /auth/login
Authenticate existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2025-11-05T..."
  }
}
```

**Errors:**
- 401 Unauthorized: Invalid credentials

---

### GET /auth/user
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2025-11-05T..."
}
```

**Errors:**
- 401 Unauthorized: Invalid or missing token

---

### POST /auth/logout
Logout current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

## Using Authentication in Routes

### Protect an endpoint with authentication:

```python
from fastapi import APIRouter, Depends
from utils.auth import verify_user, get_current_user_id

router = APIRouter()

@router.get("/protected")
async def protected_route(user: dict = Depends(verify_user)):
    """Route accessible only to authenticated users"""
    return {"user_id": user.id, "email": user.email}

@router.get("/my-data")
async def get_my_data(user_id: str = Depends(get_current_user_id)):
    """Route that needs just the user ID"""
    return {"user_id": user_id, "data": "..."}
```

## Testing with cURL

### Sign up:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Get user (with token):
```bash
curl -X GET http://localhost:8000/auth/user \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Frontend Integration Example

```javascript
// Sign up
const signup = async (email, password) => {
  const response = await fetch('http://localhost:8000/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
};

// Login
const login = async (email, password) => {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
};

// Get user
const getUser = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/auth/user', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};

// Authenticated request
const makeAuthRequest = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
};
```
