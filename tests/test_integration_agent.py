import os

import pytest

from thoughtful_agent.agent import ThoughtfulSupportAgent


@pytest.mark.integration
def test_end_to_end_predefined_dataset_answers() -> None:
    agent = ThoughtfulSupportAgent()

    cases = [
        (
            "What does the eligibility verification agent (EVA) do?",
            "EVA automates the process of verifying a patient’s eligibility and benefits information in real-time, eliminating manual data entry errors and reducing claim rejections.",
        ),
        (
            "What does the claims processing agent (CAM) do?",
            "CAM streamlines the submission and management of claims, improving accuracy, reducing manual intervention, and accelerating reimbursements.",
        ),
        (
            "How does the payment posting agent (PHIL) work?",
            "PHIL automates the posting of payments to patient accounts, ensuring fast, accurate reconciliation of payments and reducing administrative burden.",
        ),
        (
            "Tell me about Thoughtful AI's Agents.",
            "Thoughtful AI provides a suite of AI-powered automation agents designed to streamline healthcare processes. These include Eligibility Verification (EVA), Claims Processing (CAM), and Payment Posting (PHIL), among others.",
        ),
        (
            "What are the benefits of using Thoughtful AI's agents?",
            "Using Thoughtful AI's Agents can significantly reduce administrative costs, improve operational efficiency, and reduce errors in critical processes like claims management and payment posting.",
        ),
    ]

    for question, expected_answer in cases:
        response = agent.answer(question)
        assert response.source == "knowledge_base"
        assert response.answer == expected_answer


@pytest.mark.integration
def test_end_to_end_fallback_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    agent = ThoughtfulSupportAgent(threshold=0.99)

    response = agent.answer("What is the capital of France?")

    assert response.source == "llm_fallback"
    assert "set openai_api_key" in response.answer.lower()
    assert response.matched_question is None
    assert response.confidence is not None


@pytest.mark.integration
def test_end_to_end_handles_unexpected_input_type() -> None:
    agent = ThoughtfulSupportAgent()

    response = agent.answer({"bad": "input"})

    assert response.source == "validation"
    assert "text question" in response.answer.lower()


@pytest.mark.integration
@pytest.mark.live_openai
def test_live_openai_fallback_response() -> None:
    if os.getenv("RUN_LIVE_OPENAI_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_OPENAI_TESTS=1 to enable live OpenAI integration tests.")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        pytest.skip("OPENAI_API_KEY is required for live OpenAI integration tests.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("OPENAI_API_KEY", api_key)
    monkeypatch.setenv("OPENAI_MODEL", model)
    agent = ThoughtfulSupportAgent(threshold=0.99)

    response = agent.answer("In one short sentence, what is healthcare revenue cycle management?")

    assert response.source == "llm_fallback"
    assert response.answer.strip()
    assert "set openai_api_key" not in response.answer.lower()
    monkeypatch.undo()
