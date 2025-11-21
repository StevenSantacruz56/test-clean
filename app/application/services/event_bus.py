"""
Event Bus Service using package-events-bus library.

This module provides event bus functionality for publishing and subscribing to domain events.
Uses the package-events-bus library (events_bus) for event handling.
"""

from typing import Type, Callable, Any, Optional
import logging

from events_bus.core import EventBusPublisher, AsyncHandler, SyncHandler, BaseEvent
from app.core.config import settings
from app.domain.events.base_event import BaseDomainEvent

logger = logging.getLogger(__name__)


class EventBusService:
    """
    Wrapper service for package-events-bus EventBusPublisher.

    Provides a clean interface for publishing and subscribing to domain events.
    Supports both sync and async event handlers based on configuration.
    """

    def __init__(self, use_async: bool = None):
        """
        Initialize EventBus service.

        Args:
            use_async: Whether to use async event handlers. Defaults to settings.event_bus_async
        """
        self.use_async = use_async if use_async is not None else settings.event_bus_async
        self._publisher = EventBusPublisher()

        logger.info(f"Initialized EventBusService ({'async' if self.use_async else 'sync'})")

    def subscribe(
        self,
        event_type: Type[BaseDomainEvent],
        handler: Callable[[BaseDomainEvent], Any],
        priority: int = 0
    ) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The event class to subscribe to
            handler: The handler function (can be sync or async)
            priority: Handler priority (not used in package-events-bus, kept for compatibility)

        Example:
            >>> async def on_company_created(event: CompanyCreated):
            ...     print(f"Company {event.company_id} created!")
            >>>
            >>> event_bus = EventBusService()
            >>> event_bus.subscribe(CompanyCreated, on_company_created)
        """
        try:
            # Wrap handler based on type
            if self.use_async:
                # Use AsyncHandler from package-events-bus
                wrapped_handler = AsyncHandler(handler)
            else:
                # Use SyncHandler from package-events-bus
                wrapped_handler = SyncHandler(handler)

            # Register handler with the publisher
            self._publisher.register_handler(event_type, wrapped_handler)

            logger.info(
                f"Subscribed handler '{handler.__name__}' to event '{event_type.__name__}'"
            )
        except Exception as e:
            logger.error(f"Error subscribing handler to event {event_type.__name__}: {e}")
            raise

    async def publish(self, event: BaseDomainEvent) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event instance to publish

        Example:
            >>> event = CompanyCreated(company_id="123", company_name="Acme Inc", country_id="CO")
            >>> await event_bus.publish(event)
        """
        if not settings.event_bus_enabled:
            logger.debug(f"Event bus disabled. Skipping event: {event.__class__.__name__}")
            return

        try:
            event_name = event.__class__.__name__
            logger.info(f"Publishing event: {event_name}")

            # Publish using package-events-bus
            await self._publisher.publish(event)

            logger.debug(f"Event published successfully: {event_name}")

        except Exception as e:
            logger.error(f"Error publishing event {event.__class__.__name__}: {e}", exc_info=True)
            raise

    def get_publisher(self) -> EventBusPublisher:
        """Get the underlying EventBusPublisher instance."""
        return self._publisher


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
