from dataclasses import dataclass


@dataclass(frozen=True)
class QAItem:
    question: str
    answer: str


@dataclass(frozen=True)
class AgentResponse:
    answer: str
    source: str
    confidence: float | None = None
    matched_question: str | None = None
