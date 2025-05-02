class FlexBaseError(Exception):
    """Base exception for all FlexBase client errors."""
    pass

class UnauthorizedError(FlexBaseError):
    """Raised when authentication fails."""
    pass

class BadRequestError(FlexBaseError):
    """Raised when the server returns a 400 status code."""
    pass

class NotFoundError(FlexBaseError):
    """Raised when the requested resource is not found."""
    pass

class ConnectionError(FlexBaseError):
    """Raised when a connection error occurs."""
    pass

class TimeoutError(FlexBaseError):
    """Raised when a request times out."""
    pass 