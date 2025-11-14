# API Quick Start Guide

## Company Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Available Endpoints

#### 1. Create Company
**POST** `/companies/`

**Request Body:**
```json
{
  "company_name": "Tech Solutions Inc.",
  "country_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Success Response (201):**
```json
{
  "company_id": "987e6543-e21b-12d3-a456-426614174000",
  "company_name": "Tech Solutions Inc.",
  "country_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data
- `409 Conflict` - Company name already exists

---

#### 2. Update Company
**PUT** `/companies/{company_id}`

**Request Body (all fields optional):**
```json
{
  "company_name": "Tech Solutions Corp.",
  "country_id": "123e4567-e89b-12d3-a456-426614174001"
}
```

**Success Response (200):**
```json
{
  "company_id": "987e6543-e21b-12d3-a456-426614174000",
  "company_name": "Tech Solutions Corp.",
  "country_id": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data
- `404 Not Found` - Company doesn't exist
- `409 Conflict` - New name already exists

---

#### 3. Get Company
**GET** `/companies/{company_id}`

**Success Response (200):**
```json
{
  "company_id": "987e6543-e21b-12d3-a456-426614174000",
  "company_name": "Tech Solutions Corp.",
  "country_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Company doesn't exist

---

## Quick Test with cURL

### 1. Create a company
```bash
curl -X POST "http://localhost:8000/api/v1/companies/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "My Company",
    "country_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

### 2. Update the company (use the company_id from step 1)
```bash
curl -X PUT "http://localhost:8000/api/v1/companies/YOUR_COMPANY_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "My Updated Company"
  }'
```

### 3. Get the company
```bash
curl -X GET "http://localhost:8000/api/v1/companies/YOUR_COMPANY_ID"
```

---

## Interactive Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API testing
  - Try out all endpoints
  - See request/response schemas

- **ReDoc**: http://localhost:8000/redoc
  - Beautiful API documentation
  - Detailed schema information

---

## Validation Rules

### Company Name
- ✅ Required
- ✅ 1-255 characters
- ✅ Cannot be empty or whitespace only
- ✅ Must be unique

### Country ID
- ✅ Required
- ✅ Must be valid UUID format

---

## Architecture Highlights

This implementation follows **Clean Architecture + DDD + SOLID**:

✅ **Domain Layer** - Business logic isolated
✅ **Application Layer** - Use cases orchestrate workflows
✅ **Infrastructure Layer** - Database and external services
✅ **Presentation Layer** - HTTP API endpoints

✅ **Repository Pattern** - Abstract data access
✅ **Dependency Injection** - Loose coupling
✅ **Domain Events** - Track state changes
✅ **Validation** - Multiple layers of validation

---

## Error Format

All errors follow a consistent format:

```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE"
}
```

### Common Error Codes
- `COMPANY_NOT_FOUND` - Company with given ID not found
- `COMPANY_ALREADY_EXISTS` - Company name already in use
- `INVALID_COMPANY` - Invalid company data

---

## Next Steps

1. **Test the API** using Swagger UI at http://localhost:8000/docs
2. **Read the architecture** in `docs/architecture.md`
3. **See implementation details** in `IMPLEMENTATION.md`
4. **Follow best practices** in `CLAUDE.md`

---

## Getting Help

- Check `SETUP.md` for installation instructions
- Check `IMPLEMENTATION.md` for detailed architecture
- Check `docs/api.md` for full API documentation
- Check application logs for debugging

---

**Happy Coding! 🚀**
