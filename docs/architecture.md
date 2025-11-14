# Architecture Documentation

## Overview

This project follows Clean Architecture principles combined with Domain-Driven Design (DDD) and SOLID principles.

## Layers

### 1. Domain Layer
The core of the application containing business logic.
- **Entities**: Objects with unique identity
- **Value Objects**: Immutable objects compared by value
- **Aggregates**: Transactional consistency boundaries
- **Domain Services**: Business logic spanning multiple entities
- **Repositories**: Abstract interfaces for persistence
- **Events**: Domain events representing important facts
- **Specifications**: Encapsulated business rules

### 2. Application Layer
Orchestrates domain logic and coordinates workflows.
- **Use Cases**: Application services representing user actions
- **DTOs**: Data transfer objects
- **Mappers**: Convert between domain and DTOs
- **Services**: Event bus, Unit of Work

### 3. Infrastructure Layer
Technical implementations.
- **Database**: PostgreSQL and Redis connections
- **Repositories**: Concrete implementations
- **Cache**: Redis caching
- **Messaging**: Event publishing/subscription
- **External**: Third-party service integrations

### 4. Presentation Layer
API and HTTP handling.
- **Routers**: FastAPI endpoints organized by version and country
- **Schemas**: Pydantic request/response models
- **Dependencies**: Dependency injection
- **Middleware**: Error handling, logging, etc.

## Dependency Rule

Dependencies always point inward:
```
Presentation → Application → Domain ← Infrastructure
```

The domain layer has no dependencies on other layers.

## Design Patterns

- Repository Pattern
- Unit of Work
- Factory Pattern
- Specification Pattern
- Event-Driven Architecture
- Dependency Injection
- Anti-Corruption Layer

## Testing Strategy

- **Unit Tests**: Fast, isolated tests for domain and application logic
- **Integration Tests**: Tests with real database and external dependencies

See `CLAUDE.md` for detailed architecture guidelines and best practices.
