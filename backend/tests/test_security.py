"""Test SQL security validation."""

import pytest

from app.core.exceptions import SecurityException
from app.core.security import SQLSecurityValidator, validate_sql_query


class TestSQLSecurityValidator:
    """Test cases for SQL security validator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SQLSecurityValidator()

    def test_valid_select_query(self):
        """Test that valid SELECT queries pass validation."""
        queries = [
            "SELECT * FROM users",
            "SELECT id, name FROM products WHERE price > 10",
            "SELECT COUNT(*) FROM orders",
            "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id",
        ]
        for query in queries:
            is_valid, error = self.validator.validate(query)
            assert is_valid, f"Query should be valid: {query}, error: {error}"

    def test_forbidden_keywords(self):
        """Test that forbidden keywords are rejected."""
        forbidden_queries = [
            "DROP TABLE users",
            "DELETE FROM users WHERE id = 1",
            "TRUNCATE TABLE orders",
            "INSERT INTO users VALUES (1, 'test')",
            "UPDATE users SET name = 'hacked'",
            "ALTER TABLE users ADD COLUMN evil TEXT",
        ]
        for query in forbidden_queries:
            is_valid, error = self.validator.validate(query)
            assert not is_valid, f"Query should be rejected: {query}"

    def test_sql_injection_patterns(self):
        """Test that SQL injection patterns are detected."""
        injection_queries = [
            "SELECT * FROM users; DROP TABLE users",
            "SELECT * FROM users WHERE id = 1 -- comment",
            "SELECT * FROM users /* comment */ WHERE 1=1",
        ]
        for query in injection_queries:
            is_valid, error = self.validator.validate(query)
            assert not is_valid, f"Injection should be rejected: {query}"

    def test_empty_query(self):
        """Test that empty queries are rejected."""
        is_valid, error = self.validator.validate("")
        assert not is_valid
        assert "Empty" in error

    def test_sanitize(self):
        """Test query sanitization."""
        assert self.validator.sanitize("  SELECT * FROM users  ;  ") == "SELECT * FROM users"
        assert self.validator.sanitize("SELECT  *   FROM   users") == "SELECT * FROM users"


def test_validate_sql_query_raises_on_invalid():
    """Test that validate_sql_query raises SecurityException for invalid queries."""
    with pytest.raises(SecurityException):
        validate_sql_query("DROP TABLE users")
