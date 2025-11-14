# Setup Guide

Quick setup guide for the Test Clean Architecture project.

## Prerequisites

- Python 3.13+
- Docker and Docker Compose
- Poetry

## Installation Steps

### 1. Install Dependencies

```bash
poetry install
```

### 2. Start Databases

Start PostgreSQL and Redis using Docker Compose:

```bash
docker-compose up -d
```

Verify containers are running:

```bash
docker-compose ps
```

### 3. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if needed to match your configuration.

### 4. Initialize Database

Create the database tables:

```bash
poetry run python scripts/init_db.py
```

### 5. Run the Application

Start the FastAPI server:

```bash
poetry run uvicorn src.app.presentation.main:app --reload
```

Or alternatively:

```bash
cd src
poetry run uvicorn app.presentation.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing the Company Endpoints

### Create a Company

```bash
curl -X POST "http://localhost:8000/api/v1/companies/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Solutions Inc.",
    "country_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

### Get a Company

```bash
curl -X GET "http://localhost:8000/api/v1/companies/{company_id}"
```

### Update a Company

```bash
curl -X PUT "http://localhost:8000/api/v1/companies/{company_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Solutions Corp."
  }'
```

## Running Tests

Run all tests:

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=src --cov-report=html
```

## Code Quality

Format code:

```bash
poetry run ruff format .
```

Lint code:

```bash
poetry run ruff check .
```

Fix linting issues:

```bash
poetry run ruff check --fix .
```

## Troubleshooting

### Database Connection Issues

If you get database connection errors:

1. Check if PostgreSQL container is running:
   ```bash
   docker-compose ps
   ```

2. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

3. Restart containers:
   ```bash
   docker-compose restart
   ```

### Import Errors

If you get module import errors, make sure you're running from the correct directory:

```bash
# Run from project root
cd /Users/stevengarcia/Documents/Projects/test-clean

# Or add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

## Project Structure

```
src/app/
├── domain/          # Business logic (entities, aggregates, repositories)
├── application/     # Use cases, DTOs, mappers
├── infrastructure/  # Database, cache, external services
├── presentation/    # API endpoints, schemas
└── core/           # Configuration and utilities
```

## Next Steps

1. Add authentication and authorization
2. Implement more endpoints (list companies, delete company)
3. Add Redis caching
4. Implement event publishing
5. Add comprehensive tests
6. Set up CI/CD pipeline

## Additional Resources

- Architecture: See `docs/architecture.md`
- API Documentation: See `docs/api.md`
- Domain Model: See `docs/domain_model.md`
- Best Practices: See `CLAUDE.md`
