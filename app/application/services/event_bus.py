"""
Event Bus Service using package-events-bus.

This module provides event bus functionality for publishing and subscribing to domain events.
Uses the package-events-bus library for a robust event-driven architecture.
"""

from typing import Type, Callable, Any, Optional
import logging
from package_events_bus import EventBus as PackageEventBus, Event, AsyncEventBus

from app.core.config import settings

logger = logging.getLogger(__name__)


class EventBusService:
    """
    Wrapper service for package-events-bus EventBus.

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

        if self.use_async:
            self._bus = AsyncEventBus()
            logger.info("Initialized AsyncEventBus")
        else:
            self._bus = PackageEventBus()
            logger.info("Initialized EventBus (sync)")

    def subscribe(
        self,
        event_type: Type[Event],
        handler: Callable[[Event], Any],
        priority: int = 0
    ) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The event class to subscribe to
            handler: The handler function (can be sync or async based on use_async)
            priority: Handler priority (higher executes first)

        Example:
            >>> async def on_company_created(event: CompanyCreated):
            ...     print(f"Company {event.company_id} created!")
            >>>
            >>> event_bus = EventBusService()
            >>> event_bus.subscribe(CompanyCreated, on_company_created)
        """
        try:
            self._bus.subscribe(event_type, handler, priority=priority)
            logger.info(
                f"Subscribed handler '{handler.__name__}' to event '{event_type.__name__}' "
                f"with priority {priority}"
            )
        except Exception as e:
            logger.error(f"Error subscribing handler to event {event_type.__name__}: {e}")
            raise

    def unsubscribe(
        self,
        event_type: Type[Event],
        handler: Callable[[Event], Any]
    ) -> None:
        """
        Unsubscribe a handler from an event type.

        Args:
            event_type: The event class to unsubscribe from
            handler: The handler function to remove

        Example:
            >>> event_bus.unsubscribe(CompanyCreated, on_company_created)
        """
        try:
            self._bus.unsubscribe(event_type, handler)
            logger.info(f"Unsubscribed handler '{handler.__name__}' from event '{event_type.__name__}'")
        except Exception as e:
            logger.error(f"Error unsubscribing handler from event {event_type.__name__}: {e}")
            raise

    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event instance to publish

        Example:
            >>> event = CompanyCreated(company_id="123", company_name="Acme Inc")
            >>> await event_bus.publish(event)
        """
        if not settings.event_bus_enabled:
            logger.debug(f"Event bus disabled. Skipping event: {event.__class__.__name__}")
            return

        try:
            event_name = event.__class__.__name__
            logger.info(f"Publishing event: {event_name}")

            if self.use_async:
                await self._bus.publish(event)
            else:
                self._bus.publish(event)

            logger.debug(f"Event published successfully: {event_name}")
        except Exception as e:
            logger.error(f"Error publishing event {event.__class__.__name__}: {e}", exc_info=True)
            raise

    def clear_subscribers(self, event_type: Optional[Type[Event]] = None) -> None:
        """
        Clear subscribers for a specific event type or all events.

        Args:
            event_type: The event class to clear subscribers for. If None, clears all.

        Example:
            >>> event_bus.clear_subscribers(CompanyCreated)  # Clear for specific event
            >>> event_bus.clear_subscribers()  # Clear all
        """
        try:
            if event_type:
                self._bus.clear_subscribers(event_type)
                logger.info(f"Cleared subscribers for event: {event_type.__name__}")
            else:
                # Clear all subscribers
                if hasattr(self._bus, '_subscribers'):
                    self._bus._subscribers.clear()
                logger.info("Cleared all event subscribers")
        except Exception as e:
            logger.error(f"Error clearing subscribers: {e}")
            raise

    @property
    def subscriber_count(self) -> int:
        """Get total number of subscribed handlers across all events."""
        if hasattr(self._bus, '_subscribers'):
            return sum(len(handlers) for handlers in self._bus._subscribers.values())
        return 0


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
