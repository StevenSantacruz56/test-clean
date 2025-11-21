"""
Company Event Handlers.

Handlers for company domain events using package-events-bus library.
"""

import logging
from events_bus.core import AsyncHandler

from app.domain.events.company_created import CompanyCreated
from app.domain.events.company_updated import CompanyUpdated

logger = logging.getLogger(__name__)


class CompanyCreatedHandler(AsyncHandler):
    """
    Handler for CompanyCreated events.

    This handler reacts when a new company is created.
    You can add business logic here such as:
    - Sending notification emails
    - Creating audit logs
    - Triggering downstream processes
    - Updating read models
    """

    async def handle(self, event: CompanyCreated) -> None:
        """
        Handle the CompanyCreated event.

        Args:
            event: The CompanyCreated event instance
        """
        logger.info(
            f"[CompanyCreatedHandler] Processing company creation: "
            f"id={event.company_id}, name={event.company_name}"
        )

        try:
            # TODO: Add your business logic here
            # Examples:
            # - Send welcome email to company admin
            # - Create default company settings
            # - Trigger onboarding workflow
            # - Update search index
            # - Send notification to Slack/Teams

            logger.info(f"[CompanyCreatedHandler] Successfully processed company {event.company_id}")

        except Exception as e:
            logger.error(
                f"[CompanyCreatedHandler] Error processing company creation: {e}",
                exc_info=True
            )
            # Re-raise to allow event bus to handle the error
            raise


class CompanyUpdatedHandler(AsyncHandler):
    """
    Handler for CompanyUpdated events.

    This handler reacts when a company is updated.
    You can add business logic here such as:
    - Invalidating caches
    - Updating read models
    - Sending change notifications
    - Creating audit trail
    """

    async def handle(self, event: CompanyUpdated) -> None:
        """
        Handle the CompanyUpdated event.

        Args:
            event: The CompanyUpdated event instance
        """
        logger.info(
            f"[CompanyUpdatedHandler] Processing company update: "
            f"id={event.company_id}, name={event.company_name}"
        )

        try:
            # TODO: Add your business logic here
            # Examples:
            # - Invalidate company cache
            # - Update search index
            # - Send change notification email
            # - Update read models/materialized views
            # - Trigger data sync to downstream systems

            logger.info(f"[CompanyUpdatedHandler] Successfully processed company update {event.company_id}")

        except Exception as e:
            logger.error(
                f"[CompanyUpdatedHandler] Error processing company update: {e}",
                exc_info=True
            )
            # Re-raise to allow event bus to handle the error
            raise
