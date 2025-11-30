"""Azure OpenAI LLM provider."""

from openai import AsyncAzureOpenAI

from app.core.exceptions import LLMException
from app.llm.providers.base import BaseLLMProvider


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI API provider for LLM calls."""

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment: str,
        api_version: str = "2024-02-15-preview",
        temperature: float = 0.0,
        max_tokens: int = 1000
    ):
        """
        Initialize Azure OpenAI provider.
        
        Args:
            api_key: Azure OpenAI API key.
            endpoint: Azure OpenAI endpoint URL.
            deployment: Model deployment name.
            api_version: API version to use.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.
        """
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment = deployment
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, messages: list[dict[str, str]]) -> str:
        """Generate completion using Azure OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            if not response.choices:
                raise LLMException(
                    message="Azure OpenAI returned no choices",
                    details={"deployment": self.deployment}
                )

            return response.choices[0].message.content or ""

        except LLMException:
            raise
        except Exception as e:
            raise LLMException(
                message="Azure OpenAI API call failed",
                details={"error": str(e), "deployment": self.deployment}
            )

    async def is_available(self) -> bool:
        """Check if Azure OpenAI API is available."""
        try:
            # Simple test call
            await self.client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False
