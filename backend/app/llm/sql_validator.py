"""SQL query validator."""

import re
from typing import Optional

from app.config import get_settings
from app.core.security import SQLSecurityValidator
from app.models.query import SQLValidationResult

settings = get_settings()


class SQLValidator:
    """Validates SQL queries for syntax and security."""

    def __init__(self):
        """Initialize SQL validator."""
        self.security_validator = SQLSecurityValidator()

    def validate(self, sql: str) -> SQLValidationResult:
        """
        Validate SQL query for security and basic syntax.
        
        Args:
            sql: SQL query to validate.
            
        Returns:
            SQLValidationResult with validation status.
        """
        warnings = []

        # Basic syntax checks
        if not sql or not sql.strip():
            return SQLValidationResult(
                is_valid=False,
                error="Empty SQL query"
            )

        # Security validation
        is_secure, security_error = self.security_validator.validate(sql)
        if not is_secure:
            return SQLValidationResult(
                is_valid=False,
                error=security_error
            )

        # Sanitize the SQL
        sanitized_sql = self.security_validator.sanitize(sql)

        # Check for common issues
        warnings.extend(self._check_for_warnings(sanitized_sql))

        return SQLValidationResult(
            is_valid=True,
            sql=sanitized_sql,
            warnings=warnings
        )

    def _check_for_warnings(self, sql: str) -> list[str]:
        """Check for non-fatal issues in the SQL."""
        warnings = []
        sql_upper = sql.upper()

        # Check for SELECT * usage
        if re.search(r'\bSELECT\s+\*', sql_upper):
            warnings.append("Using SELECT * - consider specifying columns explicitly for better performance")

        # Check for missing LIMIT on large queries
        if "LIMIT" not in sql_upper and "COUNT(" not in sql_upper:
            warnings.append("No LIMIT clause - results may be truncated")

        # Check for potential Cartesian join
        if " JOIN " not in sql_upper and " , " in sql and sql_upper.count("FROM") == 1:
            if sql.count(",") > 0 and "WHERE" not in sql_upper:
                warnings.append("Potential Cartesian product - ensure proper JOIN conditions")

        return warnings

    def ensure_limit(self, sql: str, max_rows: int) -> str:
        """
        Ensure SQL has a LIMIT clause.
        
        Args:
            sql: SQL query.
            max_rows: Maximum rows to return.
            
        Returns:
            SQL with LIMIT clause added if not present.
        """
        if "LIMIT" not in sql.upper():
            return f"{sql} LIMIT {max_rows}"
        return sql
