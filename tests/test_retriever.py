import json
from pathlib import Path

import pytest

from thoughtful_agent.retriever import (
    _jaccard_similarity,
    _meaningful_tokens,
    _sequence_similarity,
    _tokenize,
    find_best_match,
    load_knowledge_base,
    score_query,
)
from thoughtful_agent.types import QAItem


def test_load_knowledge_base_contains_all_expected_questions() -> None:
    kb_path = Path(__file__).parents[1] / "thoughtful_agent" / "data" / "qa.json"
    kb = load_knowledge_base(kb_path)

    assert len(kb) == 5
    actual_questions = {item.question for item in kb}
    expected_questions = {
        "What does the eligibility verification agent (EVA) do?",
        "What does the claims processing agent (CAM) do?",
        "How does the payment posting agent (PHIL) work?",
        "Tell me about Thoughtful AI's Agents.",
        "What are the benefits of using Thoughtful AI's agents?",
    }
    assert actual_questions == expected_questions


def test_load_knowledge_base_file_not_found() -> None:
    with pytest.raises(ValueError, match="Knowledge base file not found"):
        load_knowledge_base(Path("/tmp/does-not-exist-qa.json"))


def test_load_knowledge_base_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError, match="not valid JSON"):
        load_knowledge_base(path)


def test_load_knowledge_base_invalid_questions_type(tmp_path: Path) -> None:
    path = tmp_path / "bad-type.json"
    path.write_text(json.dumps({"questions": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a list"):
        load_knowledge_base(path)


def test_load_knowledge_base_no_valid_entries(tmp_path: Path) -> None:
    path = tmp_path / "empty.json"
    path.write_text(
        json.dumps({"questions": [{"question": "", "answer": ""}, {"foo": "bar"}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="does not contain any valid"):
        load_knowledge_base(path)


def test_find_best_match_for_known_query() -> None:
    kb = [
        QAItem(question="What does the claims processing agent (CAM) do?", answer="CAM answer"),
        QAItem(question="How does the payment posting agent (PHIL) work?", answer="PHIL answer"),
    ]

    match, score = find_best_match("What does CAM do?", kb, threshold=0.1)

    assert match is not None
    assert match.answer == "CAM answer"
    assert score > 0


def test_find_best_match_empty_query_and_threshold_miss() -> None:
    kb = [QAItem(question="Tell me about Thoughtful AI's Agents.", answer="info")]

    empty_match, empty_score = find_best_match("   ", kb)
    assert empty_match is None
    assert empty_score == 0.0

    miss_match, miss_score = find_best_match("completely unrelated", kb, threshold=0.95)
    assert miss_match is None
    assert 0.0 <= miss_score < 0.95


def test_similarity_helpers_and_scoring() -> None:
    tokens = _tokenize("CAM, cam! EVA?")
    assert tokens == {"cam", "eva"}

    assert _jaccard_similarity(set(), {"a"}) == 0.0
    assert _jaccard_similarity({"a"}, {"a", "b"}) == 0.5

    seq = _sequence_similarity("abc", "ABC")
    assert seq == 1.0

    score_related = score_query("What does EVA do", "What does the eligibility verification agent (EVA) do?")
    score_unrelated = score_query("weather tomorrow", "What does the eligibility verification agent (EVA) do?")
    assert score_related > score_unrelated


def test_meaningful_token_gate_prevents_generic_phrase_false_match() -> None:
    meaningful = _meaningful_tokens("tell me about lions")
    assert meaningful == {"lions"}

    score = score_query("tell me about lions", "Tell me about Thoughtful AI's Agents.")
    assert score == 0.0
