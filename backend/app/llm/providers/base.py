"""Base LLM provider interface."""

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, messages: list[dict[str, str]]) -> str:
        """
        Generate a completion from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            
        Returns:
            Generated text response.
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the provider is available.
        
        Returns:
            True if available, False otherwise.
        """
        pass
