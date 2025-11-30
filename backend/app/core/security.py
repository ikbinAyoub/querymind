"""Security utilities for SQL validation and sanitization."""

import re
from typing import Set

from app.config import get_settings
from app.core.exceptions import SecurityException

settings = get_settings()


class SQLSecurityValidator:
    """Validates SQL queries for security compliance."""

    def __init__(self):
        self.forbidden_keywords: Set[str] = set(
            kw.upper() for kw in settings.forbidden_sql_keywords
        )
        self.allowed_keywords: Set[str] = set(
            kw.upper() for kw in settings.allowed_sql_keywords
        )
        
        # Patterns for detecting dangerous SQL constructs
        self.dangerous_patterns = [
            r"--",  # SQL comments
            r"/\*",  # Block comments
            r"\*/",
            r";\s*\w+",  # Multiple statements
            r"xp_\w+",  # Extended stored procedures
            r"sp_\w+",  # System stored procedures
            r"0x[0-9a-fA-F]+",  # Hex encoding
            r"char\s*\(",  # CHAR function (often used in injection)
            r"concat\s*\(.+--",  # Concat with comment
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.dangerous_patterns]

    def validate(self, sql: str) -> tuple[bool, str | None]:
        """
        Validate SQL query for security.
        
        Args:
            sql: The SQL query to validate.
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        if not sql or not sql.strip():
            return False, "Empty SQL query"

        sql_upper = sql.upper()

        # Check for forbidden keywords
        for keyword in self.forbidden_keywords:
            # Use word boundary to avoid false positives
            pattern = rf"\b{keyword}\b"
            if re.search(pattern, sql_upper):
                return False, f"Forbidden SQL keyword detected: {keyword}"

        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(sql):
                return False, f"Potentially dangerous SQL pattern detected"

        # Verify query starts with allowed keyword
        sql_stripped = sql.strip()
        first_keyword = sql_stripped.split()[0].upper() if sql_stripped.split() else ""
        
        if first_keyword not in self.allowed_keywords:
            return False, f"Query must start with an allowed keyword. Got: {first_keyword}"

        return True, None

    def sanitize(self, sql: str) -> str:
        """
        Basic sanitization of SQL query.
        
        Args:
            sql: The SQL query to sanitize.
            
        Returns:
            Sanitized SQL query.
        """
        # Remove leading/trailing whitespace
        sql = sql.strip()
        
        # Remove trailing semicolon if present
        if sql.endswith(";"):
            sql = sql[:-1].strip()
        
        # Normalize whitespace
        sql = " ".join(sql.split())
        
        return sql


def validate_sql_query(sql: str) -> str:
    """
    Validate and sanitize SQL query.
    
    Args:
        sql: The SQL query to validate.
        
    Returns:
        Sanitized SQL query.
        
    Raises:
        SecurityException: If validation fails.
    """
    validator = SQLSecurityValidator()
    
    # Sanitize first
    sanitized_sql = validator.sanitize(sql)
    
    # Then validate
    is_valid, error_message = validator.validate(sanitized_sql)
    
    if not is_valid:
        raise SecurityException(
            message="SQL security validation failed",
            details={"error": error_message, "sql": sql[:100]}  # Truncate for safety
        )
    
    return sanitized_sql
