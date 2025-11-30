"""Database connection models."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, SecretStr


class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    # Future: MYSQL = "mysql"
    # Future: MSSQL = "mssql"
    # Future: SQLITE = "sqlite"


class ConnectionConfig(BaseModel):
    """Database connection configuration."""

    db_type: DatabaseType = Field(
        default=DatabaseType.POSTGRESQL,
        description="Type of database"
    )
    host: str = Field(
        ...,
        description="Database host address",
        examples=["localhost", "db.example.com"]
    )
    port: int = Field(
        default=5432,
        ge=1,
        le=65535,
        description="Database port"
    )
    database: str = Field(
        ...,
        description="Database name",
        examples=["mydb", "postgres"]
    )
    username: str = Field(
        ...,
        description="Database username"
    )
    password: SecretStr = Field(
        ...,
        description="Database password"
    )
    ssl_mode: Optional[str] = Field(
        default=None,
        description="SSL mode for connection",
        examples=["require", "verify-full", "disable"]
    )

    def get_connection_string(self) -> str:
        """Generate database connection string."""
        password = self.password.get_secret_value()
        base_url = f"postgresql+asyncpg://{self.username}:{password}@{self.host}:{self.port}/{self.database}"
        
        if self.ssl_mode:
            base_url += f"?ssl={self.ssl_mode}"
        
        return base_url

    def get_safe_connection_string(self) -> str:
        """Generate connection string with masked password for logging."""
        return f"postgresql+asyncpg://{self.username}:***@{self.host}:{self.port}/{self.database}"


class ConnectionTestRequest(BaseModel):
    """Request model for testing database connection."""
    
    connection: ConnectionConfig


class ConnectionResponse(BaseModel):
    """Response model for connection operations."""

    success: bool = Field(
        ...,
        description="Whether the operation was successful"
    )
    message: str = Field(
        ...,
        description="Status message"
    )
    connection_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the connection session"
    )
    details: Optional[dict] = Field(
        default=None,
        description="Additional details about the connection"
    )
