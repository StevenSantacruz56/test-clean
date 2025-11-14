# Company Endpoints Implementation

This document describes the implementation of Company create and update endpoints following Clean Architecture + DDD + SOLID principles.

## Overview

Based on the database schema in `model_db.png`, we implemented a complete Company management system with create and update endpoints.

## Database Schema

The `company` table structure:
- `company_id` (UUID, PK) - Unique identifier
- `company_name` (VARCHAR) - Company name
- `country_id` (UUID, FK) - Foreign key to country
- `created_at` (TIMESTAMP) - Creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp

## Architecture Layers

### 1. Domain Layer (`src/app/domain/`)

**Entity**:
- `entities/company.py` - Company entity with business validation

**Aggregate**:
- `aggregates/company_aggregate.py` - Root aggregate maintaining transactional consistency
  - Factory method `create()` for creating new companies
  - Method `update()` for updating company information
  - Domain event registration

**Events**:
- `events/base_event.py` - Base class for all domain events
- `events/company_created.py` - Event triggered when company is created
- `events/company_updated.py` - Event triggered when company is updated

**Repository Interface**:
- `repositories/company_repository.py` - Abstract interface defining:
  - `save()` - Create or update company
  - `find_by_id()` - Find by UUID
  - `find_by_name()` - Find by name (for uniqueness check)
  - `find_all()` - List with pagination
  - `exists()` - Check existence
  - `delete()` - Remove company

**Exceptions**:
- `exceptions/domain_exception.py` - Base domain exception
- `exceptions/company_exceptions.py`:
  - `CompanyNotFoundException` - Company not found
  - `CompanyAlreadyExistsException` - Duplicate company name
  - `InvalidCompanyException` - Invalid company data

### 2. Application Layer (`src/app/application/`)

**DTOs** (`dtos/company_dto.py`):
- `CreateCompanyDTO` - Data for creating company
- `UpdateCompanyDTO` - Data for updating company
- `CompanyDTO` - Response data

**Mappers** (`mappers/company_mapper.py`):
- `CompanyMapper.to_dto()` - Convert aggregate to DTO
- `CompanyMapper.to_aggregate()` - Convert DTO to aggregate

**Use Cases** (`use_cases/company/`):
- `create_company.py` - **CreateCompanyUseCase**
  - Validates business rules
  - Checks for duplicate names
  - Creates aggregate
  - Persists to database
  - Registers domain events

- `update_company.py` - **UpdateCompanyUseCase**
  - Finds existing company
  - Validates changes
  - Checks for name conflicts
  - Updates aggregate
  - Persists changes
  - Registers domain events

- `get_company.py` - **GetCompanyUseCase**
  - Retrieves company by ID
  - Converts to DTO

### 3. Infrastructure Layer (`src/app/infrastructure/`)

**Database Models** (`database/postgres/models/`):
- `base.py` - Base model with common fields (created_at, updated_at)
- `company_model.py` - ORM model for company table

**Database Connection**:
- `database/postgres/connection.py` - Async engine setup
- `database/postgres/session.py` - Session factory and dependency

**Repository Implementation** (`repositories/`):
- `postgres_company_repository.py` - PostgreSQL implementation
  - Implements all repository interface methods
  - Handles aggregate ↔ ORM model conversion
  - Uses async SQLAlchemy

### 4. Presentation Layer (`src/app/presentation/`)

**Schemas** (`api/routers/v1/cross/schemas/company_schema.py`):
- `CompanyCreateRequest` - Request schema for POST
- `CompanyUpdateRequest` - Request schema for PUT
- `CompanyResponse` - Response schema
- `ErrorResponse` - Error response schema

**Factory** (`api/dependencies/factories/company_factory.py`):
- `CompanyFactory.create_company_use_case()` - Inject dependencies for create
- `CompanyFactory.update_company_use_case()` - Inject dependencies for update
- `CompanyFactory.get_company_use_case()` - Inject dependencies for get

**Endpoints** (`api/routers/v1/cross/companies.py`):

1. **POST /api/v1/companies/**
   - Creates a new company
   - Validates input with Pydantic
   - Checks for duplicates
   - Returns 201 Created on success
   - Returns 409 Conflict if name exists
   - Returns 400 Bad Request if invalid

2. **PUT /api/v1/companies/{company_id}**
   - Updates existing company
   - Supports partial updates (all fields optional)
   - Validates input
   - Checks for name conflicts
   - Returns 200 OK on success
   - Returns 404 Not Found if company doesn't exist
   - Returns 409 Conflict if new name exists

3. **GET /api/v1/companies/{company_id}**
   - Retrieves company by ID
   - Returns 200 OK with company data
   - Returns 404 Not Found if not exists

**Dependencies**:
- `api/dependencies/database.py` - Database session dependency

**Main Application** (`main.py`):
- FastAPI app configuration
- Router registration
- CORS middleware
- Health check endpoint

## Key Design Patterns

1. **Repository Pattern**: Abstract data access
2. **Factory Pattern**: Dependency injection
3. **Aggregate Pattern**: Transactional consistency
4. **Domain Events**: Track state changes
5. **DTO Pattern**: Layer data transfer
6. **Use Case Pattern**: Single responsibility

## SOLID Principles Applied

- **S**: Each use case has single responsibility
- **O**: Open for extension (add new use cases)
- **L**: Repository implementations are substitutable
- **I**: Small, specific interfaces
- **D**: Depend on abstractions (repository interfaces)

## Dependency Flow

```
HTTP Request
    ↓
Endpoint (Presentation)
    ↓
Factory (DI)
    ↓
Use Case (Application)
    ↓
Repository Interface (Domain) ← Repository Implementation (Infrastructure)
    ↓
Aggregate (Domain)
    ↓
Entity (Domain)
```

## Error Handling

All layers have proper error handling:
- **Domain**: Raises domain exceptions for business rule violations
- **Application**: Catches and translates domain exceptions
- **Presentation**: Converts exceptions to HTTP status codes

## Testing Strategy

Structure supports:
- **Unit Tests**: Domain logic without I/O
- **Integration Tests**: Repository with real database
- **API Tests**: Full endpoint testing

## Next Steps

To fully implement the database schema:

1. Add Company Detail endpoints
2. Add Company Person endpoints
3. Add Company Types endpoints
4. Add relationships between entities
5. Implement authentication
6. Add caching with Redis
7. Implement event publishing
8. Add comprehensive validation
9. Create migration scripts
10. Add monitoring and logging

## Benefits of This Architecture

✅ **Testable**: Easy to mock dependencies
✅ **Maintainable**: Clear separation of concerns
✅ **Scalable**: Easy to add new features
✅ **Flexible**: Can swap implementations
✅ **Clean**: Business logic isolated from infrastructure
✅ **Type-safe**: Full type hints throughout
✅ **Well-documented**: Clear code structure

## API Examples

### Create Company

```bash
curl -X POST "http://localhost:8000/api/v1/companies/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Solutions Inc.",
    "country_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

Response (201 Created):
```json
{
  "company_id": "987e6543-e21b-12d3-a456-426614174000",
  "company_name": "Tech Solutions Inc.",
  "country_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### Update Company

```bash
curl -X PUT "http://localhost:8000/api/v1/companies/987e6543-e21b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Solutions Corp."
  }'
```

Response (200 OK):
```json
{
  "company_id": "987e6543-e21b-12d3-a456-426614174000",
  "company_name": "Tech Solutions Corp.",
  "country_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

### Get Company

```bash
curl -X GET "http://localhost:8000/api/v1/companies/987e6543-e21b-12d3-a456-426614174000"
```

Response (200 OK):
```json
{
  "company_id": "987e6543-e21b-12d3-a456-426614174000",
  "company_name": "Tech Solutions Corp.",
  "country_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

## Files Created

### Domain Layer (9 files)
- `domain/entities/company.py`
- `domain/aggregates/company_aggregate.py`
- `domain/events/base_event.py`
- `domain/events/company_created.py`
- `domain/events/company_updated.py`
- `domain/repositories/company_repository.py`
- `domain/exceptions/domain_exception.py`
- `domain/exceptions/company_exceptions.py`

### Application Layer (6 files)
- `application/dtos/company_dto.py`
- `application/mappers/company_mapper.py`
- `application/use_cases/company/create_company.py`
- `application/use_cases/company/update_company.py`
- `application/use_cases/company/get_company.py`

### Infrastructure Layer (5 files)
- `infrastructure/database/postgres/models/base.py`
- `infrastructure/database/postgres/models/company_model.py`
- `infrastructure/database/postgres/connection.py`
- `infrastructure/database/postgres/session.py`
- `infrastructure/repositories/postgres_company_repository.py`

### Presentation Layer (5 files)
- `presentation/api/dependencies/database.py`
- `presentation/api/dependencies/factories/company_factory.py`
- `presentation/api/routers/v1/cross/schemas/company_schema.py`
- `presentation/api/routers/v1/cross/companies.py`
- `presentation/api/routers/v1/router.py`
- `presentation/main.py` (updated)

### Scripts (1 file)
- `scripts/init_db.py`

**Total: 26 files implementing complete Clean Architecture for Company endpoints**
