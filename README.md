# Test Clean Architecture

Clean Architecture + DDD + SOLID project with FastAPI, PostgreSQL, and Redis.

## Architecture

This project follows Clean Architecture principles with Domain-Driven Design (DDD) and SOLID principles.

### Layers

- **Domain**: Business logic core (entities, value objects, aggregates, domain services)
- **Application**: Use cases and application services
- **Infrastructure**: Technical implementations (database, cache, external services)
- **Presentation**: API endpoints and schemas

## Getting Started

### Prerequisites

- Python 3.13+
- Docker and Docker Compose
- Poetry

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```

3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

4. Start databases:
   ```bash
   docker-compose up -d
   ```

5. Run the application:
   ```bash
   poetry run uvicorn src.app.presentation.main:app --reload
   ```

## Project Structure

See `CLAUDE.md` for detailed architecture documentation and best practices.

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:
```bash
poetry run pytest
```

With coverage:
```bash
poetry run pytest --cov=src --cov-report=html
```

## Code Quality

Format and lint:
```bash
poetry run ruff check .
poetry run ruff format .
```

## License

MIT
