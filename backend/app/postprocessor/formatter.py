"""Result formatter for different output formats."""

import csv
import io
import json
from typing import Any

from app.models.query import QueryResult


class ResultFormatter:
    """Formats query results into different output formats."""

    @staticmethod
    def to_json(result: QueryResult, include_metadata: bool = True) -> str:
        """
        Format result as JSON string.
        
        Args:
            result: Query result object.
            include_metadata: Whether to include row count and column info.
            
        Returns:
            JSON string.
        """
        data = {
            "data": [
                dict(zip(result.columns, row))
                for row in result.rows
            ]
        }

        if include_metadata:
            data["metadata"] = {
                "columns": result.columns,
                "row_count": result.row_count,
                "truncated": result.truncated
            }

        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def to_csv(result: QueryResult) -> str:
        """
        Format result as CSV string.
        
        Args:
            result: Query result object.
            
        Returns:
            CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(result.columns)

        # Write data rows
        for row in result.rows:
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def to_markdown_table(result: QueryResult, max_col_width: int = 50) -> str:
        """
        Format result as Markdown table.
        
        Args:
            result: Query result object.
            max_col_width: Maximum column width.
            
        Returns:
            Markdown table string.
        """
        if not result.rows:
            return "_No results_"

        def truncate(val: Any, max_len: int) -> str:
            s = str(val) if val is not None else "NULL"
            return s[:max_len-3] + "..." if len(s) > max_len else s

        # Calculate column widths
        col_widths = [len(col) for col in result.columns]
        for row in result.rows[:100]:  # Limit for width calculation
            for i, val in enumerate(row):
                col_widths[i] = min(max_col_width, max(col_widths[i], len(str(val or ""))))

        # Build table
        lines = []

        # Header
        header = "| " + " | ".join(
            col.ljust(col_widths[i]) for i, col in enumerate(result.columns)
        ) + " |"
        lines.append(header)

        # Separator
        separator = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"
        lines.append(separator)

        # Data rows
        for row in result.rows:
            row_str = "| " + " | ".join(
                truncate(val, col_widths[i]).ljust(col_widths[i])
                for i, val in enumerate(row)
            ) + " |"
            lines.append(row_str)

        if result.truncated:
            lines.append(f"\n_Results truncated ({result.row_count} rows shown)_")

        return "\n".join(lines)

    @staticmethod
    def to_html_table(result: QueryResult) -> str:
        """
        Format result as HTML table.
        
        Args:
            result: Query result object.
            
        Returns:
            HTML table string.
        """
        if not result.rows:
            return "<p>No results</p>"

        lines = ['<table class="query-results">']

        # Header
        lines.append("  <thead><tr>")
        for col in result.columns:
            lines.append(f"    <th>{col}</th>")
        lines.append("  </tr></thead>")

        # Body
        lines.append("  <tbody>")
        for row in result.rows:
            lines.append("    <tr>")
            for val in row:
                display_val = str(val) if val is not None else "<em>NULL</em>"
                lines.append(f"      <td>{display_val}</td>")
            lines.append("    </tr>")
        lines.append("  </tbody>")

        lines.append("</table>")

        if result.truncated:
            lines.append(f"<p><em>Results truncated ({result.row_count} rows shown)</em></p>")

        return "\n".join(lines)
