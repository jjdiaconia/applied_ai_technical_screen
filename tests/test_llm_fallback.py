from __future__ import annotations

import types

from thoughtful_agent.llm_fallback import LLMFallback


class _FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class _FakeResponsesAPI:
    def __init__(self, output_text: str = "ok", should_raise: bool = False) -> None:
        self._output_text = output_text
        self._should_raise = should_raise

    def create(self, **_: object) -> _FakeResponse:
        if self._should_raise:
            raise RuntimeError("boom")
        return _FakeResponse(self._output_text)


class _FakeClient:
    def __init__(self, output_text: str = "ok", should_raise: bool = False) -> None:
        self.responses = _FakeResponsesAPI(output_text=output_text, should_raise=should_raise)


def test_generate_returns_validation_message_for_blank_prompt() -> None:
    fallback = LLMFallback()
    result = fallback.generate("   ")
    assert "share a question" in result.lower()


def test_generate_without_api_key_uses_guidance_message(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    fallback = LLMFallback()

    result = fallback.generate("General question")
    assert "openai_api_key" in result.lower()


def test_generate_with_client_success(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    fallback = LLMFallback()
    fallback.client = _FakeClient(output_text="Generated answer")

    result = fallback.generate("Tell me something")
    assert result == "Generated answer"


def test_generate_with_client_empty_output_uses_default(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    fallback = LLMFallback()
    fallback.client = _FakeClient(output_text="   ")

    result = fallback.generate("Tell me something")
    assert "could you provide a bit more detail" in result.lower()


def test_generate_with_client_exception_uses_error_message(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    fallback = LLMFallback()
    fallback.client = _FakeClient(should_raise=True)

    result = fallback.generate("Tell me something")
    assert "ran into an issue" in result.lower()
