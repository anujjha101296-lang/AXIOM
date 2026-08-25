import os
from abc import ABC, abstractmethod
import openai

class ProviderConfigurationError(RuntimeError):
    pass

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass

class OpenAILLMProvider(LLMProvider):
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ProviderConfigurationError("OPENAI_API_KEY environment variable is not set. Real model cannot be used without an API key.")
        self.client = openai.AsyncOpenAI()

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content

class MockLLMProvider(LLMProvider):
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        env = os.getenv("ENVIRONMENT", "development").lower()
        if env == "production":
            raise ProviderConfigurationError("MOCKS MUST NEVER EXECUTE IN PRODUCTION. Missing API Keys.")
        return "Mock Answer. [citation: chunk-123]"

def get_llm_provider() -> LLMProvider:
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    # In production, require actual keys.
    if env == "production":
        if os.getenv("OPENAI_API_KEY"):
            return OpenAILLMProvider()
        else:
            raise ProviderConfigurationError("PROVIDER_NOT_CONFIGURED: Production environment requires valid OPENAI_API_KEY.")
            
    # Test or Development can use mock if explicitly asked or if keys missing
    if env in ("test", "testing", "ci") or os.getenv("USE_MOCK_LLM") == "true":
        return MockLLMProvider()
        
    if os.getenv("OPENAI_API_KEY"):
        return OpenAILLMProvider()
        
    if env == "development":
        # Silently fallback to mock in dev if keys missing, based on prompt rules
        return MockLLMProvider()

    raise ProviderConfigurationError("PROVIDER_NOT_CONFIGURED: Could not resolve a valid LLM Provider.")
