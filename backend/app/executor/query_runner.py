"""Query runner for executing SQL queries."""

import time
from typing import Any

from app.config import get_settings
from app.core.exceptions import SQLExecutionException
from app.core.security import validate_sql_query
from app.db.adapters.base import BaseDatabaseAdapter
from app.llm.sql_validator import SQLValidator
from app.models.query import QueryResult

settings = get_settings()


class QueryRunner:
    """Executes validated SQL queries against the database."""

    def __init__(self, adapter: BaseDatabaseAdapter):
        """
        Initialize query runner.
        
        Args:
            adapter: Database adapter for query execution.
        """
        self.adapter = adapter
        self.validator = SQLValidator()

    async def run(
        self,
        sql: str,
        max_rows: int | None = None,
        timeout: int | None = None
    ) -> tuple[QueryResult, float]:
        """
        Execute a SQL query and return results.
        
        Args:
            sql: SQL query to execute.
            max_rows: Maximum rows to return.
            timeout: Query timeout in seconds.
            
        Returns:
            Tuple of (QueryResult, execution_time_ms).
            
        Raises:
            SecurityException: If query fails security validation.
            SQLExecutionException: If query execution fails.
        """
        # Use defaults from settings if not specified
        max_rows = max_rows or settings.max_result_rows
        timeout = timeout or settings.query_timeout

        # Validate and sanitize the query
        validated_sql = validate_sql_query(sql)

        # Ensure LIMIT clause
        validated_sql = self.validator.ensure_limit(validated_sql, max_rows)

        # Execute with timing
        start_time = time.perf_counter()
        
        try:
            columns, rows, total_count = await self.adapter.execute_query(
                sql=validated_sql,
                max_rows=max_rows,
                timeout=timeout
            )
        except Exception as e:
            raise SQLExecutionException(
                message="Query execution failed",
                details={"error": str(e), "sql": validated_sql[:200]}
            )

        execution_time = (time.perf_counter() - start_time) * 1000  # Convert to ms

        # Build result
        result = QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            truncated=total_count > max_rows
        )

        return result, execution_time
