"""
Application — Shared Exceptions

Domain-agnostic exceptions raised by application services.
These are mapped to HTTP status codes in the API layer.
"""


class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            code="NOT_FOUND",
        )


class AlreadyExistsError(AppError):
    """Resource already exists."""
    def __init__(self, resource: str, field: str, value: str) -> None:
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            code="ALREADY_EXISTS",
        )


class AuthenticationError(AppError):
    """Authentication failed."""
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class AuthorizationError(AppError):
    """Insufficient permissions."""
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message=message, code="AUTHORIZATION_ERROR")


class ValidationError(AppError):
    """Business rule validation failed."""
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR")
