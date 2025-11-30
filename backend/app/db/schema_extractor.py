"""Schema extraction utilities."""

from app.db.adapters.base import BaseDatabaseAdapter
from app.models.schema import SchemaInfo


class SchemaExtractor:
    """Utility class for schema extraction operations."""

    def __init__(self, adapter: BaseDatabaseAdapter):
        """
        Initialize schema extractor.
        
        Args:
            adapter: Database adapter to use for extraction.
        """
        self.adapter = adapter

    async def extract(self, include_row_counts: bool = False) -> SchemaInfo:
        """
        Extract schema from the database.
        
        Args:
            include_row_counts: Whether to include approximate row counts.
            
        Returns:
            SchemaInfo object with database schema.
        """
        return await self.adapter.extract_schema(include_row_counts=include_row_counts)

    async def get_schema_for_prompt(self, include_row_counts: bool = False) -> str:
        """
        Get schema as formatted text suitable for LLM prompts.
        
        Args:
            include_row_counts: Whether to include row counts.
            
        Returns:
            Formatted schema string.
        """
        schema = await self.extract(include_row_counts=include_row_counts)
        return schema.get_schema_summary()
