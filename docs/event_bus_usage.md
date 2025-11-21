# Event Bus Implementation Guide

This document explains how to use the Event Bus system integrated with the `package-events-bus` library.

## Overview

The Event Bus system provides:
- **Domain Events**: Represent important facts that occurred in the domain
- **Event Publishing**: Publish events to AWS EventBridge (production) or local storage (development)
- **Event Handlers**: React to events with custom business logic
- **Failover Mechanism**: Store events locally if AWS is unavailable

## Architecture

```
Domain Layer (Events) → Application Layer (Use Cases) → Event Bus → Event Handlers
                                                              ↓
                                                       AWS EventBridge
                                                      (or Local Failover)
```

## Event Naming Convention

All events follow this pattern:
```
[company].[service].[version].[message_type].[resource_name].[action]
```

Example: `testclean.api.1.event.company.created`

Where:
- **company**: `testclean` (application name)
- **service**: `api` (service name)
- **version**: `1` (event schema version)
- **message_type**: `event` (always "event" for domain events)
- **resource_name**: `company` (the aggregate/entity)
- **action**: `created` (past tense verb)

## How to Create a Domain Event

### 1. Define the Event Class

```python
# app/domain/events/company_created.py
from datetime import datetime
from typing import Any, Dict
from uuid import UUID
from app.domain.events.base_event import BaseDomainEvent

class CompanyCreated(BaseDomainEvent):
    """Event triggered when a company is created."""

    EVENT_NAME = "testclean.api.1.event.company.created"

    def __init__(
        self,
        company_id: UUID,
        company_name: str,
        country_id: UUID,
        event_id: str | None = None,
        occurred_at: datetime | None = None
    ):
        super().__init__(
            event_name=self.EVENT_NAME,
            event_id=event_id,
            occurred_on=occurred_at
        )
        self.company_id = company_id
        self.company_name = company_name
        self.country_id = country_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "company_id": str(self.company_id),
            "company_name": self.company_name,
            "country_id": str(self.country_id),
        })
        return data

    @classmethod
    def from_dict(cls, event_id: str, occurred_on: datetime, attributes: dict):
        """Deserialize event from dictionary."""
        return cls(
            company_id=UUID(attributes["company_id"]),
            company_name=attributes["company_name"],
            country_id=UUID(attributes["country_id"]),
            event_id=event_id,
            occurred_at=occurred_on
        )
```

### 2. Register Event in Aggregate

```python
# app/domain/aggregates/company_aggregate.py
class CompanyAggregate:
    def __init__(self):
        self._events: List = []

    @classmethod
    def create(cls, company_name: str, country_id: UUID):
        company_id = uuid4()
        aggregate = cls(company_id=company_id, ...)

        # Register the event
        aggregate._events.append(
            CompanyCreated(
                company_id=company_id,
                company_name=company_name,
                country_id=country_id
            )
        )

        return aggregate

    @property
    def events(self) -> List:
        """Get domain events."""
        return self._events.copy()

    def clear_events(self) -> None:
        """Clear events after publishing."""
        self._events.clear()
```

### 3. Publish Event in Use Case

```python
# app/application/use_cases/company/create_company.py
class CreateCompanyUseCase:
    def __init__(
        self,
        company_repository: CompanyRepository,
        event_bus: EventBusService
    ):
        self.company_repository = company_repository
        self.event_bus = event_bus

    async def execute(self, dto: CreateCompanyDTO) -> CompanyDTO:
        # Create aggregate
        company = CompanyAggregate.create(...)

        # Save to database
        saved = await self.company_repository.save(company)

        # Publish events
        for event in saved.events:
            await self.event_bus.publish(event)
        saved.clear_events()

        return CompanyMapper.to_dto(saved)
```

### 4. Create Event Handler

```python
# app/infrastructure/messaging/handlers/company_event_handlers.py
from events_bus.core import AsyncHandler
from app.domain.events.company_created import CompanyCreated
import logging

logger = logging.getLogger(__name__)

class CompanyCreatedHandler(AsyncHandler):
    """Handler for CompanyCreated events."""

    async def handle(self, event: CompanyCreated) -> None:
        """React to company creation."""
        logger.info(f"Company created: {event.company_name} (id={event.company_id})")

        # Add your business logic here:
        # - Send welcome email
        # - Create default settings
        # - Trigger onboarding workflow
        # - Update search index
        # - Send notification to Slack
```

### 5. Register Handler on Startup

```python
# app/presentation/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register event handlers
    event_bus = get_event_bus()
    event_bus.register_handler(
        CompanyCreated.EVENT_NAME,
        CompanyCreatedHandler()
    )

    yield
```

## Event Bus Configuration

### Environment Variables

```env
# Event Bus
EVENT_BUS_ENABLED=true
EVENT_BUS_ASYNC=true

# AWS Configuration (production only)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### Local Development Mode

In `localhost` environment:
- Events are stored locally (no AWS required)
- Uses `LocalFailover` to persist events
- Events are logged to console
- Perfect for development and testing

### Production Mode

In `testing/staging/production` environments:
- Events are sent to AWS EventBridge
- Uses `EventBridgePublisher` with failover
- Events can be consumed by SQS queues
- Supports retry and error handling

## Testing Events

### Unit Test Example

```python
import pytest
from app.domain.events.company_created import CompanyCreated
from uuid import UUID

def test_company_created_event():
    event = CompanyCreated(
        company_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        company_name="Test Company",
        country_id=UUID("123e4567-e89b-12d3-a456-426614174001")
    )

    assert event.event_name == "testclean.api.1.event.company.created"
    assert event.company_name == "Test Company"

    # Test serialization
    data = event.to_dict()
    assert data["company_id"] == "123e4567-e89b-12d3-a456-426614174000"
```

### Integration Test Example

```python
import pytest
from app.application.services.event_bus import EventBusService, reset_event_bus

@pytest.fixture
def event_bus():
    reset_event_bus()  # Clean state
    bus = EventBusService(use_local_mode=True)
    yield bus
    reset_event_bus()

@pytest.mark.asyncio
async def test_publish_event(event_bus):
    event = CompanyCreated(...)
    await event_bus.publish(event)
    # Event is published to local failover
```

## Dependency Injection in Factories

```python
# app/presentation/api/dependencies/factories/company_factory.py
from fastapi import Depends
from app.application.services.event_bus import get_event_bus, EventBusService

class CompanyFactory:
    @staticmethod
    def create_company_use_case(
        db: AsyncSession = Depends(get_db),
        event_bus: EventBusService = Depends(get_event_bus),
    ) -> CreateCompanyUseCase:
        repository = PostgresCompanyRepository(db)
        return CreateCompanyUseCase(
            company_repository=repository,
            event_bus=event_bus
        )
```

## Best Practices

### 1. Event Naming
- Use past tense verbs (created, updated, deleted)
- Follow the naming convention strictly
- Version your events (v1, v2) for breaking changes

### 2. Event Content
- Include all necessary data to handle the event
- Don't include sensitive information in events
- Make events serializable (use primitives or UUIDs)

### 3. Event Handlers
- Keep handlers idempotent (can run multiple times safely)
- Handle errors gracefully (log and don't re-raise unless critical)
- Avoid long-running operations in handlers
- Don't modify the event object

### 4. Use Cases
- Always publish events after successful persistence
- Clear events from aggregate after publishing
- Don't publish events if transaction fails

### 5. Testing
- Test event serialization/deserialization
- Test handlers independently
- Use `reset_event_bus()` between tests
- Mock external dependencies in handlers

## Troubleshooting

### Events Not Being Published

1. Check `EVENT_BUS_ENABLED=true` in environment
2. Verify event_bus is injected in use case
3. Check logs for error messages
4. Ensure events are added to aggregate before saving

### Handlers Not Triggered

1. Verify handlers are registered in `lifespan()`
2. Check event name matches exactly
3. Ensure handler is async (extends `AsyncHandler`)
4. Check handler logs for errors

### AWS EventBridge Issues

1. Verify AWS credentials are configured
2. Check IAM permissions for EventBridge
3. Verify EventBridge bus exists
4. Check AWS region configuration

## Advanced Usage

### Custom Event Bus Instance

```python
from app.application.services.event_bus import EventBusService

# Create custom event bus
custom_bus = EventBusService(
    bus_name="custom-bus",
    source="custom.service",
    use_local_mode=False  # Force AWS mode
)
```

### Batch Publishing

```python
events = [event1, event2, event3]
await event_bus.publish_batch(events)
```

### Retrieve Events from Failover

```python
# Get events that failed to publish
failover = event_bus.get_failover()
failed_events = failover.consume(total_events=10)

# Retry publishing
event_bus._publisher.publish_from_failover(total_events=10)
```

## References

- **package-events-bus**: https://pypi.org/project/package-events-bus/
- **AWS EventBridge**: https://aws.amazon.com/eventbridge/
- **Domain Events Pattern**: https://martinfowler.com/eaaDev/DomainEvent.html
