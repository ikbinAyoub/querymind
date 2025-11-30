"""Custom exceptions for the SQL-RAG system."""

from typing import Any


class SQLRAGException(Exception):
    """Base exception for SQL-RAG system."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConnectionException(SQLRAGException):
    """Exception raised for database connection errors."""
    pass


class SchemaExtractionException(SQLRAGException):
    """Exception raised for schema extraction errors."""
    pass


class SQLGenerationException(SQLRAGException):
    """Exception raised for SQL generation errors."""
    pass


class SQLValidationException(SQLRAGException):
    """Exception raised when SQL validation fails."""
    pass


class SQLExecutionException(SQLRAGException):
    """Exception raised for SQL execution errors."""
    pass


class SecurityException(SQLRAGException):
    """Exception raised for security violations."""
    pass


class LLMException(SQLRAGException):
    """Exception raised for LLM-related errors."""
    pass


class CacheException(SQLRAGException):
    """Exception raised for cache-related errors."""
    pass
