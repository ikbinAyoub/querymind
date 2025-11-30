"""SQL Generator using LLM providers."""

import re
from typing import Optional

from app.config import get_settings
from app.core.exceptions import LLMException, SQLGenerationException
from app.llm.prompt_builder import PromptBuilder
from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.openai import OpenAIProvider
from app.models.schema import SchemaInfo

settings = get_settings()


class SQLGenerator:
    """Generates SQL queries from natural language using LLM."""

    def __init__(
        self,
        schema: SchemaInfo,
        provider: Optional[BaseLLMProvider] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize SQL generator.
        
        Args:
            schema: Database schema information.
            provider: LLM provider to use. Defaults to configured provider.
            api_key: Optional user-provided API key (overrides env config).
        """
        self.schema = schema
        self.prompt_builder = PromptBuilder(schema)
        self.api_key = api_key
        self.provider = provider or self._get_default_provider()

    def _get_default_provider(self) -> BaseLLMProvider:
        """Get the default LLM provider based on configuration."""
        # Use user-provided API key if available, otherwise fall back to env
        api_key = self.api_key
        
        if settings.llm_provider == "openai":
            if not api_key and settings.openai_api_key:
                api_key = settings.openai_api_key.get_secret_value()
            if not api_key:
                raise LLMException(
                    message="OpenAI API key not configured. Please provide your API key.",
                    details={"provider": "openai"}
                )
            return OpenAIProvider(
                api_key=api_key,
                model=settings.openai_model
            )
        elif settings.llm_provider == "azure_openai":
            if not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
                raise LLMException(
                    message="Azure OpenAI configuration incomplete",
                    details={"provider": "azure_openai"}
                )
            from app.llm.providers.azure_openai import AzureOpenAIProvider
            return AzureOpenAIProvider(
                api_key=settings.azure_openai_api_key.get_secret_value(),
                endpoint=settings.azure_openai_endpoint,
                deployment=settings.azure_openai_deployment,
                api_version=settings.azure_openai_api_version
            )
        else:
            raise LLMException(
                message=f"Unknown LLM provider: {settings.llm_provider}",
                details={"provider": settings.llm_provider}
            )

    async def generate_sql(
        self,
        question: str,
        max_rows: int = 100
    ) -> str:
        """
        Generate SQL from a natural language question.
        
        Args:
            question: Natural language question.
            max_rows: Maximum rows for the query result.
            
        Returns:
            Generated SQL query.
            
        Raises:
            SQLGenerationException: If SQL generation fails.
        """
        try:
            messages = self.prompt_builder.build_sql_generation_prompt(
                question=question,
                include_examples=True,
                max_rows=max_rows
            )

            response = await self.provider.generate(messages)
            sql = self._clean_sql_response(response)

            if not sql:
                raise SQLGenerationException(
                    message="LLM returned empty SQL response",
                    details={"question": question}
                )

            return sql

        except LLMException:
            raise
        except Exception as e:
            raise SQLGenerationException(
                message="Failed to generate SQL query",
                details={"error": str(e), "question": question}
            )

    async def generate_explanation(
        self,
        question: str,
        sql: str,
        result_summary: str
    ) -> str:
        """
        Generate natural language explanation of query results.
        
        Args:
            question: Original question.
            sql: Generated SQL query.
            result_summary: Summary of query results.
            
        Returns:
            Natural language explanation.
        """
        try:
            messages = self.prompt_builder.build_explanation_prompt(
                question=question,
                sql=sql,
                result_summary=result_summary
            )

            return await self.provider.generate(messages)

        except Exception as e:
            # Non-critical error - return a generic message
            return f"Query executed successfully. Found {result_summary}"

    def _clean_sql_response(self, response: str) -> str:
        """
        Clean the SQL response from the LLM.
        
        Args:
            response: Raw response from LLM.
            
        Returns:
            Cleaned SQL query.
        """
        sql = response.strip()

        # Remove markdown code blocks if present
        sql = re.sub(r'^```sql\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'^```\s*', '', sql)
        sql = re.sub(r'\s*```$', '', sql)

        # Remove any trailing semicolons (we'll add them if needed)
        sql = sql.rstrip(';').strip()

        # Remove any leading/trailing whitespace and normalize
        sql = ' '.join(sql.split())

        return sql
