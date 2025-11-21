"""
Event Bus Service.

This module provides event bus functionality for publishing and subscribing to domain events.
Implements a simple in-memory event bus with support for both sync and async handlers.
"""

from typing import Type, Callable, Any, Optional, Dict, List
import logging
import asyncio
from dataclasses import dataclass

from app.core.config import settings
from app.domain.events.base_event import BaseDomainEvent

logger = logging.getLogger(__name__)


@dataclass
class EventHandler:
    """Wrapper for event handler with priority."""

    handler: Callable[[BaseDomainEvent], Any]
    priority: int = 0


class EventBusService:
    """
    In-memory Event Bus implementation.

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
        self._subscribers: Dict[Type[BaseDomainEvent], List[EventHandler]] = {}
        logger.info(f"Initialized EventBus ({'async' if self.use_async else 'sync'})")

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
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            event_handler = EventHandler(handler=handler, priority=priority)
            self._subscribers[event_type].append(event_handler)

            # Sort by priority (higher first)
            self._subscribers[event_type].sort(key=lambda h: h.priority, reverse=True)

            logger.info(
                f"Subscribed handler '{handler.__name__}' to event '{event_type.__name__}' "
                f"with priority {priority}"
            )
        except Exception as e:
            logger.error(f"Error subscribing handler to event {event_type.__name__}: {e}")
            raise

    def unsubscribe(
        self,
        event_type: Type[BaseDomainEvent],
        handler: Callable[[BaseDomainEvent], Any]
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
            if event_type in self._subscribers:
                self._subscribers[event_type] = [
                    h for h in self._subscribers[event_type] if h.handler != handler
                ]
                logger.info(f"Unsubscribed handler '{handler.__name__}' from event '{event_type.__name__}'")
        except Exception as e:
            logger.error(f"Error unsubscribing handler from event {event_type.__name__}: {e}")
            raise

    async def publish(self, event: BaseDomainEvent) -> None:
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
            event_type = type(event)
            event_name = event_type.__name__
            logger.info(f"Publishing event: {event_name}")

            if event_type not in self._subscribers:
                logger.debug(f"No subscribers for event: {event_name}")
                return

            handlers = self._subscribers[event_type]
            logger.debug(f"Found {len(handlers)} handler(s) for event: {event_name}")

            # Execute handlers based on async mode
            for event_handler in handlers:
                handler = event_handler.handler
                try:
                    if self.use_async:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            # Run sync handler in executor
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, handler, event)
                    else:
                        if asyncio.iscoroutinefunction(handler):
                            logger.warning(
                                f"Async handler '{handler.__name__}' called in sync mode. "
                                f"Consider setting event_bus_async=True"
                            )
                            asyncio.run(handler(event))
                        else:
                            handler(event)

                    logger.debug(f"Handler '{handler.__name__}' executed successfully for event: {event_name}")

                except Exception as e:
                    logger.error(
                        f"Error in handler '{handler.__name__}' for event {event_name}: {e}",
                        exc_info=True
                    )
                    # Continue with other handlers even if one fails

            logger.debug(f"Event published successfully: {event_name}")

        except Exception as e:
            logger.error(f"Error publishing event {event.__class__.__name__}: {e}", exc_info=True)
            raise

    def clear_subscribers(self, event_type: Optional[Type[BaseDomainEvent]] = None) -> None:
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
                if event_type in self._subscribers:
                    del self._subscribers[event_type]
                logger.info(f"Cleared subscribers for event: {event_type.__name__}")
            else:
                self._subscribers.clear()
                logger.info("Cleared all event subscribers")
        except Exception as e:
            logger.error(f"Error clearing subscribers: {e}")
            raise

    @property
    def subscriber_count(self) -> int:
        """Get total number of subscribed handlers across all events."""
        return sum(len(handlers) for handlers in self._subscribers.values())

    def get_subscribers(self, event_type: Type[BaseDomainEvent]) -> List[Callable]:
        """Get all handlers subscribed to an event type."""
        if event_type in self._subscribers:
            return [h.handler for h in self._subscribers[event_type]]
        return []


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
