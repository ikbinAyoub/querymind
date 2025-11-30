"""Result handler for processing query results."""

from typing import Any

from app.models.query import QueryResult


class ResultHandler:
    """Handles and transforms query results."""

    @staticmethod
    def to_dict_list(result: QueryResult) -> list[dict[str, Any]]:
        """
        Convert query result to list of dictionaries.
        
        Args:
            result: Query result object.
            
        Returns:
            List of row dictionaries.
        """
        return [
            dict(zip(result.columns, row))
            for row in result.rows
        ]

    @staticmethod
    def get_summary(result: QueryResult) -> str:
        """
        Generate a summary of query results for LLM explanation.
        
        Args:
            result: Query result object.
            
        Returns:
            Summary string.
        """
        if result.row_count == 0:
            return "No results found."

        summary_parts = [f"{result.row_count} row(s) returned"]

        if result.truncated:
            summary_parts.append("(results truncated)")

        # Add column info
        summary_parts.append(f"Columns: {', '.join(result.columns)}")

        # Add sample data for small result sets
        if result.row_count <= 5:
            sample_data = []
            for row in result.rows:
                row_str = ", ".join(f"{col}={val}" for col, val in zip(result.columns, row))
                sample_data.append(f"  [{row_str}]")
            summary_parts.append("Data:\n" + "\n".join(sample_data))
        else:
            # Just show first row as example
            first_row = result.rows[0]
            row_str = ", ".join(f"{col}={val}" for col, val in zip(result.columns, first_row))
            summary_parts.append(f"First row: [{row_str}]")

        return "\n".join(summary_parts)

    @staticmethod
    def aggregate_numeric_columns(result: QueryResult) -> dict[str, dict[str, float]]:
        """
        Calculate basic statistics for numeric columns.
        
        Args:
            result: Query result object.
            
        Returns:
            Dictionary of column names to statistics.
        """
        stats = {}

        for col_idx, col_name in enumerate(result.columns):
            values = []
            for row in result.rows:
                val = row[col_idx]
                if isinstance(val, (int, float)) and val is not None:
                    values.append(float(val))

            if values:
                stats[col_name] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "sum": sum(values),
                    "count": len(values)
                }

        return stats
