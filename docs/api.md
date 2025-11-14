# API Documentation

## Base URL

Development: `http://localhost:8000`

## API Versioning

The API is versioned and organized by country:

- `/api/v1/co/*` - Colombia-specific endpoints
- `/api/v1/mx/*` - Mexico-specific endpoints
- `/api/v1/*` - Cross-country endpoints

## Interactive Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints (Example Structure)

### Users

#### Colombia
- `POST /api/v1/co/users` - Create user
- `GET /api/v1/co/users/{id}` - Get user
- `PUT /api/v1/co/users/{id}` - Update user
- `DELETE /api/v1/co/users/{id}` - Delete user
- `GET /api/v1/co/users` - List users

#### Mexico
- `POST /api/v1/mx/users` - Create user
- `GET /api/v1/mx/users/{id}` - Get user
- `PUT /api/v1/mx/users/{id}` - Update user
- `DELETE /api/v1/mx/users/{id}` - Delete user
- `GET /api/v1/mx/users` - List users

### Orders

#### Colombia
- `POST /api/v1/co/orders` - Create order
- `GET /api/v1/co/orders/{id}` - Get order
- `POST /api/v1/co/orders/{id}/cancel` - Cancel order
- `GET /api/v1/co/orders` - List orders

### Products (Cross-country)

- `GET /api/v1/products` - List all products
- `GET /api/v1/products/{id}` - Get product details

### Health Check (Cross-country)

- `GET /api/v1/health` - Health check endpoint

## Authentication

TBD - Will use JWT tokens

## Error Responses

All errors follow a standard format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
