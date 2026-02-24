from thoughtful_agent.presentation import build_response_meta, response_notice
from thoughtful_agent.types import AgentResponse


def test_build_response_meta_for_no_match_fallback() -> None:
    response = AgentResponse(answer="fallback", source="llm_fallback", confidence=0.1234, matched_question=None)

    meta = build_response_meta(response)

    assert meta["source"] == "llm_fallback"
    assert meta["confidence"] == 0.123
    assert meta["matched_question"] is None
    assert meta["no_direct_match"] is True


def test_response_notice_variants() -> None:
    validation_notice = response_notice(AgentResponse(answer="enter question", source="validation"))
    assert validation_notice == ("info", "enter question")

    fallback_notice = response_notice(AgentResponse(answer="fallback", source="llm_fallback"))
    assert fallback_notice == (
        "warning",
        "No direct match found in the predefined dataset. Using OpenAI fallback response.",
    )

    error_notice = response_notice(AgentResponse(answer="boom", source="error"))
    assert error_notice == ("error", "boom")

    kb_notice = response_notice(AgentResponse(answer="ok", source="knowledge_base"))
    assert kb_notice is None
