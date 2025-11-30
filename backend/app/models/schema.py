"""Database schema models."""

from typing import Optional

from pydantic import BaseModel, Field


class ColumnInfo(BaseModel):
    """Information about a database column."""

    name: str = Field(
        ...,
        description="Column name"
    )
    data_type: str = Field(
        ...,
        description="Column data type"
    )
    is_nullable: bool = Field(
        default=True,
        description="Whether the column allows NULL values"
    )
    is_primary_key: bool = Field(
        default=False,
        description="Whether the column is a primary key"
    )
    is_foreign_key: bool = Field(
        default=False,
        description="Whether the column is a foreign key"
    )
    foreign_key_table: Optional[str] = Field(
        default=None,
        description="Referenced table if this is a foreign key"
    )
    foreign_key_column: Optional[str] = Field(
        default=None,
        description="Referenced column if this is a foreign key"
    )
    default_value: Optional[str] = Field(
        default=None,
        description="Default value for the column"
    )
    description: Optional[str] = Field(
        default=None,
        description="Column description/comment"
    )


class TableInfo(BaseModel):
    """Information about a database table."""

    name: str = Field(
        ...,
        description="Table name"
    )
    schema_name: str = Field(
        default="public",
        description="Schema name containing the table"
    )
    columns: list[ColumnInfo] = Field(
        default_factory=list,
        description="List of columns in the table"
    )
    row_count: Optional[int] = Field(
        default=None,
        description="Approximate number of rows in the table"
    )
    description: Optional[str] = Field(
        default=None,
        description="Table description/comment"
    )

    @property
    def full_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.schema_name}.{self.name}"


class SchemaInfo(BaseModel):
    """Complete database schema information."""

    database_name: str = Field(
        ...,
        description="Name of the database"
    )
    tables: list[TableInfo] = Field(
        default_factory=list,
        description="List of tables in the database"
    )
    extracted_at: str = Field(
        ...,
        description="Timestamp when schema was extracted"
    )

    def get_table(self, table_name: str) -> Optional[TableInfo]:
        """Get table info by name."""
        for table in self.tables:
            if table.name == table_name or table.full_name == table_name:
                return table
        return None

    def get_schema_summary(self) -> str:
        """Get compact schema summary for LLM prompts - token optimized."""
        lines = []
        for table in self.tables:
            # Kompaktes Format: table(col1:type, col2:type[PK])
            cols = []
            for col in table.columns:
                # Kurzform für Typen
                short_type = self._short_type(col.data_type)
                col_str = f"{col.name}:{short_type}"
                if col.is_primary_key:
                    col_str += "[PK]"
                elif col.is_foreign_key:
                    col_str += f"[FK->{col.foreign_key_table}]"
                cols.append(col_str)
            lines.append(f"{table.name}({', '.join(cols)})")
        return "\n".join(lines)

    def _short_type(self, data_type: str) -> str:
        """Convert data type to short form for token saving."""
        type_map = {
            "integer": "int", "bigint": "int", "smallint": "int",
            "character varying": "str", "varchar": "str", "text": "str",
            "boolean": "bool", "numeric": "num", "decimal": "num",
            "real": "num", "double precision": "num",
            "timestamp without time zone": "ts", "timestamp with time zone": "ts",
            "date": "date", "uuid": "uuid", "json": "json", "jsonb": "json",
        }
        return type_map.get(data_type.lower(), data_type[:4])
