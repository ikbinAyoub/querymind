"""PostgreSQL database adapter implementation."""

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.exceptions import (
    ConnectionException,
    SchemaExtractionException,
    SQLExecutionException,
)
from app.db.adapters.base import BaseDatabaseAdapter
from app.models.connection import ConnectionConfig
from app.models.schema import ColumnInfo, SchemaInfo, TableInfo


class PostgreSQLAdapter(BaseDatabaseAdapter):
    """PostgreSQL database adapter using asyncpg via SQLAlchemy."""

    def __init__(self, config: ConnectionConfig):
        """Initialize PostgreSQL adapter."""
        super().__init__(config)
        self._engine: AsyncEngine | None = None

    async def connect(self) -> bool:
        """Establish connection to PostgreSQL database."""
        try:
            connection_string = self.config.get_connection_string()
            self._engine = create_async_engine(
                connection_string,
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
            )
            # Test the connection
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            raise ConnectionException(
                message="Failed to connect to PostgreSQL database",
                details={"error": str(e), "host": self.config.host}
            )

    async def disconnect(self) -> None:
        """Close the database connection."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None

    async def test_connection(self) -> tuple[bool, str]:
        """Test the database connection."""
        try:
            if not self._engine:
                await self.connect()
            
            async with self._engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
            
            return True, f"Connected successfully. {version}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    async def get_database_version(self) -> str:
        """Get PostgreSQL version string."""
        if not self._engine:
            await self.connect()
        
        async with self._engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            return result.scalar() or "Unknown"

    async def extract_schema(self, include_row_counts: bool = False) -> SchemaInfo:
        """Extract database schema from PostgreSQL."""
        try:
            if not self._engine:
                await self.connect()

            tables = await self._get_tables()
            
            for table in tables:
                table.columns = await self._get_columns(table.schema_name, table.name)
                
                if include_row_counts:
                    table.row_count = await self._get_row_count(table.schema_name, table.name)

            return SchemaInfo(
                database_name=self.config.database,
                tables=tables,
                extracted_at=datetime.utcnow().isoformat()
            )
        except Exception as e:
            raise SchemaExtractionException(
                message="Failed to extract database schema",
                details={"error": str(e)}
            )

    async def _get_tables(self) -> list[TableInfo]:
        """Get list of tables from the database."""
        query = """
            SELECT 
                table_schema,
                table_name,
                obj_description((table_schema || '.' || table_name)::regclass) as table_comment
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name
        """
        
        async with self._engine.begin() as conn:
            result = await conn.execute(text(query))
            rows = result.fetchall()
        
        tables = []
        for row in rows:
            tables.append(TableInfo(
                name=row[1],
                schema_name=row[0],
                description=row[2]
            ))
        
        return tables

    async def _get_columns(self, schema_name: str, table_name: str) -> list[ColumnInfo]:
        """Get column information for a table."""
        # Query for columns with primary key and foreign key info
        query = """
            WITH pk_columns AS (
                SELECT 
                    kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = :schema_name
                    AND tc.table_name = :table_name
            ),
            fk_columns AS (
                SELECT 
                    kcu.column_name,
                    ccu.table_name AS foreign_table,
                    ccu.column_name AS foreign_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu 
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = :schema_name
                    AND tc.table_name = :table_name
            )
            SELECT 
                c.column_name,
                c.data_type,
                c.is_nullable = 'YES' as is_nullable,
                c.column_default,
                pk.column_name IS NOT NULL as is_primary_key,
                fk.column_name IS NOT NULL as is_foreign_key,
                fk.foreign_table,
                fk.foreign_column,
                col_description(
                    (c.table_schema || '.' || c.table_name)::regclass,
                    c.ordinal_position
                ) as column_comment
            FROM information_schema.columns c
            LEFT JOIN pk_columns pk ON pk.column_name = c.column_name
            LEFT JOIN fk_columns fk ON fk.column_name = c.column_name
            WHERE c.table_schema = :schema_name
                AND c.table_name = :table_name
            ORDER BY c.ordinal_position
        """
        
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text(query),
                {"schema_name": schema_name, "table_name": table_name}
            )
            rows = result.fetchall()
        
        columns = []
        for row in rows:
            columns.append(ColumnInfo(
                name=row[0],
                data_type=row[1],
                is_nullable=row[2],
                default_value=row[3],
                is_primary_key=row[4],
                is_foreign_key=row[5],
                foreign_key_table=row[6],
                foreign_key_column=row[7],
                description=row[8]
            ))
        
        return columns

    async def _get_row_count(self, schema_name: str, table_name: str) -> int:
        """Get approximate row count for a table."""
        # Use statistics for approximate count (faster than COUNT(*))
        query = """
            SELECT reltuples::bigint AS estimate
            FROM pg_class
            WHERE oid = :full_table_name::regclass
        """
        
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text(query),
                {"full_table_name": f"{schema_name}.{table_name}"}
            )
            row = result.fetchone()
        
        return int(row[0]) if row and row[0] else 0

    async def execute_query(
        self,
        sql: str,
        max_rows: int = 1000,
        timeout: int = 30
    ) -> tuple[list[str], list[list[Any]], int]:
        """Execute a SQL query and return results."""
        try:
            if not self._engine:
                await self.connect()

            # Add LIMIT if not already present and max_rows specified
            sql_lower = sql.lower()
            if "limit" not in sql_lower and max_rows:
                sql = f"{sql} LIMIT {max_rows + 1}"  # +1 to detect truncation

            async with self._engine.begin() as conn:
                # Set statement timeout
                await conn.execute(
                    text(f"SET statement_timeout = '{timeout * 1000}'")
                )
                
                result = await conn.execute(text(sql))
                
                # Get column names
                columns = list(result.keys())
                
                # Fetch rows
                rows = result.fetchall()
                
                # Reset timeout
                await conn.execute(text("SET statement_timeout = 0"))

            # Convert rows to lists and handle truncation
            total_count = len(rows)
            if total_count > max_rows:
                rows = rows[:max_rows]
            
            row_data = [[self._serialize_value(val) for val in row] for row in rows]
            
            return columns, row_data, total_count

        except Exception as e:
            raise SQLExecutionException(
                message="Failed to execute SQL query",
                details={"error": str(e), "sql": sql[:200]}
            )

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a database value for JSON output."""
        if value is None:
            return None
        if isinstance(value, (datetime,)):
            return value.isoformat()
        if isinstance(value, bytes):
            return value.hex()
        if isinstance(value, (int, float, str, bool)):
            return value
        return str(value)
