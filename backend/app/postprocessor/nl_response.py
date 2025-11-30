"""Natural language response generator."""

from app.executor.result_handler import ResultHandler
from app.llm.sql_generator import SQLGenerator
from app.models.query import QueryResult
from app.models.schema import SchemaInfo


class NLResponseGenerator:
    """Generates natural language responses for query results."""

    def __init__(self, schema: SchemaInfo, api_key: str = None):
        """
        Initialize NL response generator.
        
        Args:
            schema: Database schema information.
            api_key: Optional user-provided API key.
        """
        self.schema = schema
        self.api_key = api_key
        self.sql_generator = SQLGenerator(schema, api_key=api_key)

    async def generate(
        self,
        question: str,
        sql: str,
        result: QueryResult
    ) -> str:
        """
        Generate natural language explanation of results.
        
        Args:
            question: Original question.
            sql: Generated SQL query.
            result: Query result.
            
        Returns:
            Natural language explanation.
        """
        # Get result summary
        summary = ResultHandler.get_summary(result)

        # Generate explanation using LLM
        explanation = await self.sql_generator.generate_explanation(
            question=question,
            sql=sql,
            result_summary=summary
        )

        return explanation

    @staticmethod
    def generate_simple_response(result: QueryResult) -> str:
        """
        Generate a simple response without LLM.
        
        Args:
            result: Query result.
            
        Returns:
            Simple response string.
        """
        if result.row_count == 0:
            return "The query returned no results."
        elif result.row_count == 1:
            # Single row - format nicely
            row = result.rows[0]
            if len(result.columns) == 1:
                return f"The result is: {row[0]}"
            else:
                parts = [f"{col}: {val}" for col, val in zip(result.columns, row)]
                return "Result: " + ", ".join(parts)
        else:
            msg = f"Found {result.row_count} result(s)"
            if result.truncated:
                msg += " (results were truncated)"
            return msg + "."
