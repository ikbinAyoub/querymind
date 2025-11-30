"""Query request and response models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.connection import ConnectionConfig


class QueryRequest(BaseModel):
    """Request model for natural language query."""

    connection: ConnectionConfig = Field(
        ...,
        description="Database connection configuration"
    )
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural language question about the data",
        examples=[
            "How many users registered last month?",
            "What are the top 10 products by sales?",
            "Show me the average order value by country"
        ]
    )
    api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (optional, uses server default if not provided)"
    )
    include_sql: bool = Field(
        default=True,
        description="Include generated SQL in response"
    )
    include_explanation: bool = Field(
        default=True,
        description="Include natural language explanation of results"
    )
    max_rows: Optional[int] = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of rows to return"
    )


class QueryResult(BaseModel):
    """Query result data."""

    columns: list[str] = Field(
        ...,
        description="Column names"
    )
    rows: list[list[Any]] = Field(
        ...,
        description="Result rows as list of lists"
    )
    row_count: int = Field(
        ...,
        description="Number of rows returned"
    )
    truncated: bool = Field(
        default=False,
        description="Whether results were truncated due to max_rows limit"
    )


class QueryResponse(BaseModel):
    """Response model for query operations."""

    success: bool = Field(
        ...,
        description="Whether the query was successful"
    )
    question: str = Field(
        ...,
        description="Original natural language question"
    )
    generated_sql: Optional[str] = Field(
        default=None,
        description="SQL query generated from the question"
    )
    result: Optional[QueryResult] = Field(
        default=None,
        description="Query results"
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Natural language explanation of the results"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if query failed"
    )
    execution_time_ms: Optional[float] = Field(
        default=None,
        description="Query execution time in milliseconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the query"
    )


class SQLValidationResult(BaseModel):
    """Result of SQL validation."""

    is_valid: bool = Field(
        ...,
        description="Whether the SQL is valid and safe"
    )
    sql: Optional[str] = Field(
        default=None,
        description="Sanitized SQL if valid"
    )
    error: Optional[str] = Field(
        default=None,
        description="Validation error message"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings about the SQL"
    )
