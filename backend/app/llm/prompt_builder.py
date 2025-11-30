"""Prompt builder for LLM-based SQL generation - Token-optimized."""

from typing import Optional

from app.models.schema import SchemaInfo


class PromptBuilder:
    """Builds minimal prompts for LLM SQL generation."""

    # Kompakter System-Prompt (~100 Tokens statt ~200)
    SYSTEM_PROMPT = """SQL generator for PostgreSQL. Output ONLY executable SQL.
Rules: SELECT only, no INSERT/UPDATE/DELETE/DROP. Use exact column names from schema."""

    def __init__(self, schema: SchemaInfo):
        self.schema = schema

    def build_sql_generation_prompt(
        self,
        question: str,
        include_examples: bool = False,  # Default auf False geändert
        max_rows: Optional[int] = 100
    ) -> list[dict[str, str]]:
        """Build minimal prompt for SQL generation."""
        
        # Kompaktes Schema-Format
        schema_compact = self._build_compact_schema()
        
        # Ein einziger User-Prompt mit allem
        user_content = f"""Schema:
{schema_compact}

Q: {question}
LIMIT {max_rows}"""

        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

    def build_explanation_prompt(
        self,
        question: str,
        sql: str,
        result_summary: str
    ) -> list[dict[str, str]]:
        """Build minimal prompt for result explanation."""
        return [
            {"role": "system", "content": "Explain query results in 1-2 sentences. Be concise."},
            {"role": "user", "content": f"Q: {question}\nResult: {result_summary}"}
        ]

    def _build_compact_schema(self) -> str:
        """Build ultra-compact schema representation."""
        lines = []
        for table in self.schema.tables:
            # Format: table_name(col1:type, col2:type[PK], col3:type[FK->other])
            cols = []
            for col in table.columns:
                col_str = f"{col.name}:{self._short_type(col.data_type)}"
                if col.is_primary_key:
                    col_str += "[PK]"
                elif col.is_foreign_key:
                    col_str += f"[FK->{col.foreign_key_table}]"
                cols.append(col_str)
            
            lines.append(f"{table.name}({', '.join(cols)})")
        
        return "\n".join(lines)

    def _short_type(self, data_type: str) -> str:
        """Convert data type to short form."""
        type_map = {
            "integer": "int",
            "bigint": "int",
            "smallint": "int",
            "character varying": "str",
            "varchar": "str",
            "text": "str",
            "boolean": "bool",
            "numeric": "num",
            "decimal": "num",
            "real": "num",
            "double precision": "num",
            "timestamp without time zone": "ts",
            "timestamp with time zone": "ts",
            "date": "date",
            "time": "time",
            "uuid": "uuid",
            "json": "json",
            "jsonb": "json",
        }
        return type_map.get(data_type.lower(), data_type[:4])

    def _build_schema_context(self) -> str:
        """Legacy method - redirects to compact version."""
        return self._build_compact_schema()

    def _get_few_shot_examples(self) -> list[dict[str, str]]:
        """Not used in optimized version."""
        return []
