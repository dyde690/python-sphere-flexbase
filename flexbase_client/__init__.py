from .client import FlexBaseClient, SearchQuery
from .exceptions import (
    FlexBaseError,
    UnauthorizedError,
    BadRequestError,
    NotFoundError,
    ConnectionError,
    TimeoutError
)

__version__ = "0.2.0"
__all__ = [
    "FlexBaseClient",
    "SearchQuery",
    "FlexBaseError",
    "UnauthorizedError",
    "BadRequestError",
    "NotFoundError",
    "ConnectionError",
    "TimeoutError"
]
 