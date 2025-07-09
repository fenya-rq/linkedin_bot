from typing import Any


class CaptchaSolverError(Exception):
    """Custom exception for CAPTCHA solving errors."""

    def __init__(
        self, message: str = 'Failed to handle CAPTCHA.', details: dict[str, Any] | None = None
    ) -> None:
        """
        Initialize CAPTCHA solver error.

        :param message: Error message
        :param details: Additional error details
        """
        self._message = message
        self.details = details or {}
        super().__init__(self._message)

    @property
    def message(self) -> str:
        """
        Format the error message with details.

        :returns: Formatted error message with details
        """
        result = self._message
        for k, v in self.details.items():
            result += f'\n{k}: {v}'
        return result


class JSONNotFoundError(Exception):
    pass
