from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from thoughtful_agent.types import QAItem


TOKEN_PATTERN = re.compile(r"[a-z0-9']+")
STOPWORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "can",
    "does",
    "for",
    "how",
    "i",
    "in",
    "is",
    "me",
    "of",
    "or",
    "tell",
    "the",
    "to",
    "what",
    "work",
    "using",
    "do",
}


def load_knowledge_base(path: Path) -> list[QAItem]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Knowledge base file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Knowledge base file is not valid JSON: {path}") from exc

    raw_questions = payload.get("questions", [])
    if not isinstance(raw_questions, list):
        raise ValueError("Knowledge base JSON must contain a list under 'questions'.")

    kb: list[QAItem] = []
    for item in raw_questions:
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if question and answer:
            kb.append(QAItem(question=question, answer=answer))

    if not kb:
        raise ValueError("Knowledge base does not contain any valid question/answer entries.")

    return kb


def _tokenize(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(text.lower()))


def _meaningful_tokens(text: str) -> set[str]:
    return {token for token in _tokenize(text) if token not in STOPWORDS and len(token) > 2}


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _sequence_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def score_query(query: str, candidate_question: str) -> float:
    query_meaningful = _meaningful_tokens(query)
    candidate_meaningful = _meaningful_tokens(candidate_question)
    if query_meaningful and candidate_meaningful and not (query_meaningful & candidate_meaningful):
        return 0.0

    query_tokens = _tokenize(query)
    candidate_tokens = _tokenize(candidate_question)
    jaccard = _jaccard_similarity(query_tokens, candidate_tokens)
    sequence = _sequence_similarity(query, candidate_question)
    return (0.65 * jaccard) + (0.35 * sequence)


def find_best_match(query: str, knowledge_base: list[QAItem], threshold: float = 0.33) -> tuple[QAItem | None, float]:
    cleaned_query = query.strip()
    if not cleaned_query:
        return None, 0.0

    best_item: QAItem | None = None
    best_score = 0.0

    for item in knowledge_base:
        current_score = score_query(cleaned_query, item.question)
        if current_score > best_score:
            best_item = item
            best_score = current_score

    if best_item is None or best_score < threshold:
        return None, best_score

    return best_item, best_score
