"""
Event Bus Service using package-events-bus library.

This module provides event bus functionality for publishing and subscribing to domain events.
Uses the package-events-bus library for event handling with AWS EventBridge integration.
"""

import logging
from typing import Optional

from events_bus.aws.event_bridge_publisher import EventBridgePublisher
from events_bus.core import EventHandlerRegistry, AsyncHandler, SyncHandler, BaseHandler
from events_bus.core.infrastructure.local_failover import LocalFailover

from app.core.config import settings
from app.domain.events.base_event import BaseDomainEvent

logger = logging.getLogger(__name__)


class EventBusService:
    """
    Wrapper service for package-events-bus EventBridgePublisher.

    Provides a clean interface for publishing and subscribing to domain events.
    Uses AWS EventBridge in production or local failover for development.

    For development/localhost: Uses LocalFailover (stores events locally without AWS)
    For production: Uses EventBridge + Redis/Local Failover
    """

    def __init__(
        self,
        bus_name: str | None = None,
        source: str | None = None,
        use_local_mode: bool | None = None
    ):
        """
        Initialize EventBus service.

        Args:
            bus_name: EventBridge bus name (defaults to 'default' for localhost, configured for production)
            source: Event source identifier (defaults to app_name.service)
            use_local_mode: Force local mode without AWS (None = auto-detect from environment)
        """
        self.bus_name = bus_name or (
            "default" if settings.is_localhost() else f"{settings.app_name}-{settings.environment}"
        )
        self.source = source or f"{settings.app_name}.{settings.service}"
        self.use_local_mode = use_local_mode if use_local_mode is not None else settings.is_localhost()

        # Initialize publisher based on environment
        if self.use_local_mode:
            logger.info("Initializing EventBus in LOCAL mode (no AWS required)")
            # In local mode, we use LocalFailover to store events without actually sending them
            self._failover = LocalFailover()
            self._publisher = self._create_local_publisher()
        else:
            logger.info(f"Initializing EventBus with EventBridge: {self.bus_name}")
            self._failover = LocalFailover()  # Can be replaced with RedisFailover in production
            self._publisher = EventBridgePublisher(
                bus_name=self.bus_name,
                source=self.source,
                failover=self._failover,
                aws_region_name=settings.aws_region
            )

        logger.info(f"EventBusService initialized (local_mode={self.use_local_mode})")

    def _create_local_publisher(self) -> EventBridgePublisher:
        """
        Create a local mock publisher for development.

        This publisher will store events in LocalFailover instead of sending to AWS.
        """

        class LocalEventBridgePublisher(EventBridgePublisher):
            """Local development publisher that doesn't require AWS."""

            def __init__(self, bus_name: str, source: str, failover):
                self.bus_name = bus_name
                self.source = source
                self.failover = failover
                self.aws_region_name = "local"
                # Don't call _load_client() to avoid AWS dependency

            def publish(self, event: BaseDomainEvent, wait_time: int | None = None):
                """Store event locally instead of publishing to EventBridge."""
                from events_bus.core.infrastructure.event_serializer import EventJsonSerializer

                event_serialized = EventJsonSerializer.serialize(event)
                logger.info(
                    f"[LOCAL MODE] Event published: {event.event_name} (id={event.event_id})"
                )
                logger.debug(f"[LOCAL MODE] Event data: {event_serialized}")

                # Store in failover for later retrieval if needed
                self.failover.publish(event.event_id, event.event_name, event_serialized)

            def publish_batch(self, events: list[BaseDomainEvent]):
                """Publish batch of events locally."""
                for event in events:
                    self.publish(event)

            def publish_from_failover(self, total_events: int):
                """Retrieve events from failover."""
                events = self.failover.consume(total_events)
                logger.info(f"[LOCAL MODE] Retrieved {len(events)} events from failover")
                return events

        return LocalEventBridgePublisher(
            bus_name=self.bus_name,
            source=self.source,
            failover=self._failover
        )

    def register_handler(
        self,
        event_name: str,
        handler: BaseHandler,
    ) -> None:
        """
        Register a handler for a specific event type.

        Args:
            event_name: The event name to listen for (e.g., "testclean.api.1.event.company.created")
            handler: Handler instance (SyncHandler or AsyncHandler)

        Example:
            >>> class CompanyCreatedHandler(AsyncHandler):
            ...     async def handle(self, event: CompanyCreated):
            ...         print(f"Company {event.company_id} created!")
            >>>
            >>> event_bus = EventBusService()
            >>> handler = CompanyCreatedHandler()
            >>> event_bus.register_handler(CompanyCreated.EVENT_NAME, handler)
        """
        try:
            EventHandlerRegistry.register_handler(event_name, handler)
            logger.info(f"Registered handler '{handler.__class__.__name__}' for event '{event_name}'")
        except ValueError as e:
            logger.warning(f"Handler already registered: {e}")
        except Exception as e:
            logger.error(f"Error registering handler for event {event_name}: {e}")
            raise

    def register_multiple_handlers(self, handlers: list[tuple[str, BaseHandler]]) -> None:
        """
        Register multiple handlers at once.

        Args:
            handlers: List of tuples with (event_name, handler)

        Example:
            >>> handlers = [
            ...     (CompanyCreated.EVENT_NAME, CompanyCreatedHandler()),
            ...     (CompanyUpdated.EVENT_NAME, CompanyUpdatedHandler()),
            ... ]
            >>> event_bus.register_multiple_handlers(handlers)
        """
        EventHandlerRegistry.register_multiple_handlers(handlers)
        logger.info(f"Registered {len(handlers)} handlers")

    async def publish(self, event: BaseDomainEvent) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The domain event instance to publish

        Example:
            >>> event = CompanyCreated(
            ...     company_id=UUID("..."),
            ...     company_name="Acme Inc",
            ...     country_id=UUID("...")
            ... )
            >>> await event_bus.publish(event)
        """
        if not settings.event_bus_enabled:
            logger.debug(f"Event bus disabled. Skipping event: {event.event_name}")
            return

        try:
            logger.info(f"Publishing event: {event.event_name} (id={event.event_id})")

            # Publish using EventBridge (or local mock)
            self._publisher.publish(event)

            # Trigger registered handlers (if any)
            await self._trigger_handlers(event)

            logger.debug(f"Event published successfully: {event.event_name}")

        except Exception as e:
            logger.error(f"Error publishing event {event.event_name}: {e}", exc_info=True)
            # Don't re-raise to avoid breaking the main flow
            # Event is stored in failover for retry

    async def publish_batch(self, events: list[BaseDomainEvent]) -> None:
        """
        Publish multiple events at once.

        Args:
            events: List of domain events to publish
        """
        if not settings.event_bus_enabled:
            logger.debug("Event bus disabled. Skipping batch publish")
            return

        try:
            logger.info(f"Publishing batch of {len(events)} events")
            self._publisher.publish_batch(events)

            # Trigger handlers for each event
            for event in events:
                await self._trigger_handlers(event)

            logger.debug(f"Batch published successfully: {len(events)} events")

        except Exception as e:
            logger.error(f"Error publishing batch: {e}", exc_info=True)

    async def _trigger_handlers(self, event: BaseDomainEvent) -> None:
        """
        Trigger all registered handlers for an event.

        Args:
            event: The event to handle
        """
        handlers = EventHandlerRegistry.get_handlers_by_event(event.event_name)

        if not handlers:
            logger.debug(f"No handlers registered for event: {event.event_name}")
            return

        logger.debug(f"Triggering {len(handlers)} handlers for event: {event.event_name}")

        for handler in handlers:
            try:
                if isinstance(handler, AsyncHandler):
                    await handler.handle(event)
                elif isinstance(handler, SyncHandler):
                    handler.handle(event)
                else:
                    logger.warning(f"Unknown handler type: {type(handler)}")

            except Exception as e:
                logger.error(
                    f"Error in handler {handler.__class__.__name__} for event {event.event_name}: {e}",
                    exc_info=True
                )
                # Continue with other handlers

    def get_publisher(self) -> EventBridgePublisher:
        """Get the underlying EventBridgePublisher instance."""
        return self._publisher

    def get_failover(self) -> LocalFailover:
        """Get the failover mechanism."""
        return self._failover


# Global event bus instance
_event_bus_instance: Optional[EventBusService] = None


def get_event_bus() -> EventBusService:
    """
    Get or create the global EventBus instance.

    This ensures a single EventBus is shared across the application.

    Returns:
        EventBusService: The global event bus instance

    Example:
        >>> event_bus = get_event_bus()
        >>> await event_bus.publish(some_event)
    """
    global _event_bus_instance

    if _event_bus_instance is None:
        _event_bus_instance = EventBusService()
        logger.info("Created global EventBus instance")

    return _event_bus_instance


def reset_event_bus() -> None:
    """
    Reset the global event bus instance.

    Useful for testing to ensure clean state between tests.
    """
    global _event_bus_instance
    _event_bus_instance = None
    logger.info("Reset global EventBus instance")
