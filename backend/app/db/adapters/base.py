"""Abstract base class for database adapters."""

from abc import ABC, abstractmethod
from typing import Any

from app.models.connection import ConnectionConfig
from app.models.schema import SchemaInfo


class BaseDatabaseAdapter(ABC):
    """Abstract base class for database adapters."""

    def __init__(self, config: ConnectionConfig):
        """
        Initialize the adapter with connection configuration.
        
        Args:
            config: Database connection configuration.
        """
        self.config = config
        self._engine = None
        self._connection = None

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the database.
        
        Returns:
            True if connection successful, False otherwise.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    async def test_connection(self) -> tuple[bool, str]:
        """
        Test the database connection.
        
        Returns:
            Tuple of (success, message).
        """
        pass

    @abstractmethod
    async def extract_schema(self, include_row_counts: bool = False) -> SchemaInfo:
        """
        Extract database schema information.
        
        Args:
            include_row_counts: Whether to include approximate row counts.
            
        Returns:
            SchemaInfo object containing database schema.
        """
        pass

    @abstractmethod
    async def execute_query(
        self,
        sql: str,
        max_rows: int = 1000,
        timeout: int = 30
    ) -> tuple[list[str], list[list[Any]], int]:
        """
        Execute a SQL query and return results.
        
        Args:
            sql: The SQL query to execute.
            max_rows: Maximum number of rows to return.
            timeout: Query timeout in seconds.
            
        Returns:
            Tuple of (column_names, rows, total_row_count).
        """
        pass

    @abstractmethod
    async def get_database_version(self) -> str:
        """
        Get the database version string.
        
        Returns:
            Database version string.
        """
        pass

    @property
    def is_connected(self) -> bool:
        """Check if currently connected to database."""
        return self._engine is not None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
