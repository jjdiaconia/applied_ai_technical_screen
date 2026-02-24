from __future__ import annotations

from thoughtful_agent.types import AgentResponse


def build_response_meta(response: AgentResponse) -> dict[str, object]:
    return {
        "source": response.source,
        "confidence": round(response.confidence, 3) if response.confidence is not None else None,
        "matched_question": response.matched_question,
        "no_direct_match": response.source == "llm_fallback" and response.matched_question is None,
    }


def response_notice(response: AgentResponse) -> tuple[str, str] | None:
    if response.source == "validation":
        return "info", response.answer
    if response.source == "llm_fallback":
        return "warning", "No direct match found in the predefined dataset. Showing fallback response."
    if response.source == "error":
        return "error", response.answer
    return None
