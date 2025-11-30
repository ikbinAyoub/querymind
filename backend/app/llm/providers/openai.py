"""OpenAI LLM provider."""

from typing import Optional

from openai import AsyncOpenAI

from app.core.exceptions import LLMException
from app.llm.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider for LLM calls."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.0,
        max_tokens: int = 1000
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key.
            model: Model to use (e.g., 'gpt-4', 'gpt-3.5-turbo').
            temperature: Sampling temperature (0.0 for deterministic).
            max_tokens: Maximum tokens in response.
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, messages: list[dict[str, str]]) -> str:
        """Generate completion using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            if not response.choices:
                raise LLMException(
                    message="OpenAI returned no choices",
                    details={"model": self.model}
                )

            return response.choices[0].message.content or ""

        except LLMException:
            raise
        except Exception as e:
            raise LLMException(
                message="OpenAI API call failed",
                details={"error": str(e), "model": self.model}
            )

    async def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
