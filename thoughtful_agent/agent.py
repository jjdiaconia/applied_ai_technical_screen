from __future__ import annotations

from pathlib import Path

from thoughtful_agent.llm_fallback import LLMFallback
from thoughtful_agent.retriever import find_best_match, load_knowledge_base
from thoughtful_agent.types import AgentResponse, QAItem


class ThoughtfulSupportAgent:
    def __init__(
        self,
        kb_path: Path | None = None,
        threshold: float = 0.33,
    ) -> None:
        default_path = Path(__file__).parent / "data" / "qa.json"
        self.kb_path = kb_path or default_path
        self.threshold = threshold
        self.knowledge_base: list[QAItem] = load_knowledge_base(self.kb_path)
        self.llm_fallback = LLMFallback()

    def answer(self, user_input: object) -> AgentResponse:
        if not isinstance(user_input, str):
            return AgentResponse(
                answer="Please enter a text question and I’ll do my best to help.",
                source="validation",
            )

        cleaned_input = user_input.strip()
        if not cleaned_input:
            return AgentResponse(
                answer="Please enter a question and I’ll do my best to help.",
                source="validation",
            )

        try:
            match, score = find_best_match(cleaned_input, self.knowledge_base, threshold=self.threshold)
        except Exception:
            return AgentResponse(
                answer="I ran into an internal issue while searching the knowledge base. Please try again.",
                source="error",
            )

        if match is not None:
            return AgentResponse(
                answer=match.answer,
                source="knowledge_base",
                confidence=score,
                matched_question=match.question,
            )

        try:
            llm_answer = self.llm_fallback.generate(cleaned_input)
        except Exception:
            return AgentResponse(
                answer="I couldn't generate a fallback response right now. Please try again shortly.",
                source="error",
                confidence=score,
            )

        return AgentResponse(
            answer=llm_answer,
            source="llm_fallback",
            confidence=score,
        )
