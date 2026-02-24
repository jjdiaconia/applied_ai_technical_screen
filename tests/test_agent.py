from thoughtful_agent.agent import ThoughtfulSupportAgent


def test_returns_knowledge_base_answers_for_all_predefined_questions() -> None:
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
        assert response.matched_question is not None
        assert response.confidence is not None
        assert response.confidence > 0


def test_returns_validation_for_empty_input() -> None:
    agent = ThoughtfulSupportAgent()
    response = agent.answer("   ")

    assert response.source == "validation"
    assert "enter a question" in response.answer.lower()


def test_uses_llm_fallback_when_no_match(monkeypatch) -> None:
    agent = ThoughtfulSupportAgent(threshold=0.99)
    monkeypatch.setattr(agent.llm_fallback, "generate", lambda _: "fallback response")

    response = agent.answer("What is the weather in Boston?")

    assert response.source == "llm_fallback"
    assert response.answer == "fallback response"
    assert response.matched_question is None


def test_tell_me_about_lions_does_not_match_thoughtful_dataset(monkeypatch) -> None:
    agent = ThoughtfulSupportAgent()
    monkeypatch.setattr(agent.llm_fallback, "generate", lambda _: "lions fallback")

    response = agent.answer("tell me about lions")

    assert response.source == "llm_fallback"
    assert response.answer == "lions fallback"
    assert response.matched_question is None


def test_handles_invalid_non_string_input_gracefully() -> None:
    agent = ThoughtfulSupportAgent()

    response = agent.answer(None)

    assert response.source == "validation"
    assert "text question" in response.answer.lower()


def test_handles_search_layer_error_gracefully(monkeypatch) -> None:
    agent = ThoughtfulSupportAgent()

    def _raise(*args, **kwargs):
        raise RuntimeError("search failed")

    monkeypatch.setattr("thoughtful_agent.agent.find_best_match", _raise)

    response = agent.answer("Tell me about CAM")

    assert response.source == "error"
    assert "internal issue" in response.answer.lower()


def test_handles_fallback_layer_error_gracefully(monkeypatch) -> None:
    agent = ThoughtfulSupportAgent(threshold=0.99)

    def _raise(_):
        raise RuntimeError("fallback failed")

    monkeypatch.setattr(agent.llm_fallback, "generate", _raise)

    response = agent.answer("What is an unrelated question?")

    assert response.source == "error"
    assert "fallback response" in response.answer.lower()
