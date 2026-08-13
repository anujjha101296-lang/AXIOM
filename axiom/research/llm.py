import os
from abc import ABC, abstractmethod
import openai

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass

class OpenAILLMProvider(LLMProvider):
    def __init__(self):
        self.client = openai.AsyncOpenAI()

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content

class MockLLMProvider(LLMProvider):
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        return "Mock Answer. [citation: chunk-123]"

def get_llm_provider() -> LLMProvider:
    if os.getenv("ENVIRONMENT") == "test" or not os.getenv("OPENAI_API_KEY"):
        return MockLLMProvider()
    return OpenAILLMProvider()
