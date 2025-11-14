"""
Base Domain Exception.

Base exception class for all domain-specific exceptions.
"""


class DomainException(Exception):
    """
    Base exception for domain layer.

    All domain-specific exceptions should inherit from this class.
    """

    def __init__(self, message: str):
        """
        Initialize domain exception.

        Args:
            message: Error message
        """
        self.message = message
        super().__init__(self.message)
