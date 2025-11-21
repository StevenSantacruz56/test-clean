# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure following Clean Architecture + DDD + SOLID principles
- Complete layer architecture: Domain, Application, Infrastructure, Presentation
- Company entity with create and update endpoints
- PostgreSQL database integration with SQLAlchemy async
- **Event Bus System** using package-events-bus library
  - Integration with AWS EventBridge for production environments
  - Local failover mode for development (no AWS required)
  - Event naming convention: `[company].[service].[version].[type].[resource].[action]`
  - Automatic event publishing in use cases
  - Event handler registration system
- **Domain Events** with proper implementation
  - CompanyCreated event (testclean.api.1.event.company.created)
  - CompanyUpdated event (testclean.api.1.event.company.updated)
  - BaseDomainEvent implementing package-events-bus BaseEvent interface
  - Event serialization/deserialization support
- **Event Handlers**
  - CompanyCreatedHandler for reacting to company creation
  - CompanyUpdatedHandler for reacting to company updates
  - Async handler support with error handling
  - Handler registration in application lifespan
- Repository pattern implementation
- Use case pattern for business logic
- Dependency injection with FastAPI
- API endpoints:
  - POST /api/v1/companies - Create company (publishes CompanyCreated event)
  - PUT /api/v1/companies/{company_id} - Update company (publishes CompanyUpdated event)
  - GET /api/v1/companies/{company_id} - Get company by ID
- Comprehensive error handling
- Pydantic schemas for request/response validation
- Database initialization script

### Infrastructure
- PostgreSQL async connection and session management
- Repository implementation with domain aggregate conversion
- ORM models for company table
- **EventBusService** wrapper for package-events-bus
  - AWS EventBridge publisher integration
  - Local development mode without AWS
  - Event handler registry
  - Failover mechanism for failed events
- **Event Messaging Infrastructure**
  - Event handlers in infrastructure/messaging/handlers
  - Event registration in application startup

### Documentation
- Architecture documentation
- API documentation
- Domain model documentation
- CLAUDE.md with best practices and guidelines
- **Event Bus Usage Guide** (docs/event_bus_usage.md)
  - Complete guide on creating and publishing events
  - Event handler implementation examples
  - Testing strategies for events
  - Troubleshooting guide
  - Best practices for event-driven architecture

### Changed
- **BaseDomainEvent**: Now properly extends package-events-bus BaseEvent
  - Supports event_name, event_id, occurred_on attributes
  - Implements to_dict() and from_dict() methods
  - Compatible with EventBridge serialization
- **Company Use Cases**: Now publish domain events after persistence
  - CreateCompanyUseCase publishes CompanyCreated event
  - UpdateCompanyUseCase publishes CompanyUpdated event
  - Events are cleared from aggregate after publishing
- **Company Factory**: Injects EventBusService into use cases
- **Application Startup**: Registers event handlers on lifespan startup
- **CORS Configuration**: Fixed to use list format instead of string

### Fixed
- Event naming to follow package-events-bus convention
- Event serialization for AWS EventBridge compatibility
- Aggregate event management (events property and clear_events method)

## [0.1.0] - 2024-01-01

### Added
- Initial project setup
- Basic directory structure
- Configuration files (pyproject.toml, docker-compose.yml)
- Testing structure (unit and integration tests)
