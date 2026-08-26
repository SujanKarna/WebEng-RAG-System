import requests

from src.config.settings import (
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT,
)


class LLMClient:
    """
    Client for communicating with a locally hosted LLM
    through the LM Studio OpenAI-compatible API.
    """

    def __init__(
        self,
        base_url: str = LLM_BASE_URL,
        model: str = LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
        timeout: int = LLM_TIMEOUT,
    ):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        response = requests.post(
            self.base_url,
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"].strip()

        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                "Unexpected response format from LM Studio."
            ) from exc