"""Connection manager for handling database connections."""

import hashlib
import uuid
from typing import Dict, Optional

from app.core.exceptions import ConnectionException
from app.db.adapters.base import BaseDatabaseAdapter
from app.db.adapters.postgres import PostgreSQLAdapter
from app.models.connection import ConnectionConfig, DatabaseType


class ConnectionManager:
    """Manages database connections and adapter instantiation."""

    _adapters: Dict[DatabaseType, type[BaseDatabaseAdapter]] = {
        DatabaseType.POSTGRESQL: PostgreSQLAdapter,
    }

    def __init__(self):
        """Initialize connection manager."""
        self._active_connections: Dict[str, BaseDatabaseAdapter] = {}

    def get_adapter_class(self, db_type: DatabaseType) -> type[BaseDatabaseAdapter]:
        """
        Get the appropriate adapter class for a database type.
        
        Args:
            db_type: The database type.
            
        Returns:
            The adapter class for the database type.
            
        Raises:
            ConnectionException: If database type is not supported.
        """
        if db_type not in self._adapters:
            raise ConnectionException(
                message=f"Database type '{db_type}' is not supported",
                details={"supported_types": list(self._adapters.keys())}
            )
        return self._adapters[db_type]

    def create_adapter(self, config: ConnectionConfig) -> BaseDatabaseAdapter:
        """
        Create a new database adapter instance.
        
        Args:
            config: Database connection configuration.
            
        Returns:
            Database adapter instance.
        """
        adapter_class = self.get_adapter_class(config.db_type)
        return adapter_class(config)

    def generate_connection_id(self, config: ConnectionConfig) -> str:
        """
        Generate a unique connection ID based on config.
        
        Args:
            config: Database connection configuration.
            
        Returns:
            Unique connection identifier.
        """
        # Create hash from connection details (excluding password)
        connection_str = f"{config.db_type}:{config.host}:{config.port}:{config.database}:{config.username}"
        hash_str = hashlib.sha256(connection_str.encode()).hexdigest()[:12]
        return f"conn_{hash_str}_{uuid.uuid4().hex[:8]}"

    async def test_connection(self, config: ConnectionConfig) -> tuple[bool, str, Optional[str]]:
        """
        Test a database connection.
        
        Args:
            config: Database connection configuration.
            
        Returns:
            Tuple of (success, message, connection_id if successful).
        """
        adapter = self.create_adapter(config)
        
        try:
            success, message = await adapter.test_connection()
            
            if success:
                connection_id = self.generate_connection_id(config)
                return True, message, connection_id
            
            return False, message, None
        finally:
            await adapter.disconnect()

    async def get_connection(self, config: ConnectionConfig) -> BaseDatabaseAdapter:
        """
        Get a database connection, creating if necessary.
        
        Args:
            config: Database connection configuration.
            
        Returns:
            Connected database adapter.
        """
        adapter = self.create_adapter(config)
        await adapter.connect()
        return adapter


# Global connection manager instance
connection_manager = ConnectionManager()
