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
- Domain events system (CompanyCreated, CompanyUpdated)
- Repository pattern implementation
- Use case pattern for business logic
- Dependency injection with FastAPI
- API endpoints:
  - POST /api/v1/companies - Create company
  - PUT /api/v1/companies/{company_id} - Update company
  - GET /api/v1/companies/{company_id} - Get company by ID
- Comprehensive error handling
- Pydantic schemas for request/response validation
- Database initialization script

### Infrastructure
- PostgreSQL async connection and session management
- Repository implementation with domain aggregate conversion
- ORM models for company table

### Documentation
- Architecture documentation
- API documentation
- Domain model documentation
- CLAUDE.md with best practices and guidelines

## [0.1.0] - 2024-01-01

### Added
- Initial project setup
- Basic directory structure
- Configuration files (pyproject.toml, docker-compose.yml)
- Testing structure (unit and integration tests)
