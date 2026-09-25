"""Rerank — xếp hạng lại kết quả (slide 39, slide 44 Irrelevant Retrieval).

Bản cơ bản: thưởng thêm điểm cho đoạn có tiêu đề (tài liệu hoặc mục) chứa từ của truy vấn. Mặc định
tắt (``RERANK_ENABLED=false``): bật lên rồi đo lại là một thí nghiệm ở Workbook 3.
"""

from __future__ import annotations

from src.retrieval.models import Hit
from src.retrieval.search import tokenize


def rerank(hits: list[Hit], query: str, *, title_bonus: float = 0.05) -> list[Hit]:
    """Cộng ``title_bonus`` nhân với tỉ lệ từ truy vấn có trong tiêu đề, rồi sắp lại."""
    q_tokens = set(tokenize(query))
    if not q_tokens:
        return hits
    boosted: list[Hit] = []
    for h in hits:
        title_tokens = set(tokenize(f"{h.doc_title} {h.section}"))
        bonus = title_bonus * len(q_tokens & title_tokens) / len(q_tokens)
        boosted.append(
            Hit(
                chunk_id=h.chunk_id,
                doc_id=h.doc_id,
                doc_title=h.doc_title,
                section=h.section,
                version=h.version,
                effective_date=h.effective_date,
                text=h.text,
                score=round(min(1.0, h.score + bonus), 4),
                category=h.category,
            )
        )
    return sorted(boosted, key=lambda h: h.score, reverse=True)
