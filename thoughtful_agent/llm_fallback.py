from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMFallback:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate(self, user_input: str) -> str:
        prompt = user_input.strip()
        if not prompt:
            return "Please share a question so I can help."

        if self.client is None:
            return (
                "I can answer detailed questions about Thoughtful AI's agents right now. "
                "For broader topics, set OPENAI_API_KEY to enable full LLM fallback responses."
            )

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are a concise, helpful customer support assistant. "
                            "Provide accurate, easy-to-understand responses."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            return response.output_text.strip() or "I can help with that—could you provide a bit more detail?"
        except Exception:
            return (
                "I ran into an issue generating a fallback response. "
                "Please try again, or ask about Thoughtful AI's agents for a direct answer from the knowledge base."
            )
