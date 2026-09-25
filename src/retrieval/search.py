"""Retrieve — ba cách tìm của slide 40: keyword, semantic và hybrid.

* keyword: tỉ lệ từ của truy vấn xuất hiện trong đoạn. Tốt với tên gói, mã, thuật ngữ chính xác.
* semantic: độ giống nhau về nghĩa giữa vector truy vấn và vector đoạn (cosine). Bắt được câu hỏi
  diễn đạt khác tài liệu.
* hybrid: trộn hai điểm theo trọng số ``vector_weight`` (SPEC-RAG-02).
"""

from __future__ import annotations

import math
import re
from typing import Any

from src.retrieval.models import Hit

_WORD = re.compile(r"[0-9a-zA-ZÀ-ỹ]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Tách văn bản thành các từ viết thường."""
    return [t.lower() for t in _WORD.findall(text)]


def chunk_tokens(chunk: dict[str, Any]) -> set[str]:
    """Tập từ của một đoạn (tiêu đề tài liệu, tiêu đề mục và nội dung). Tính một lần rồi nhớ lại."""
    if "_tokens" not in chunk:
        chunk["_tokens"] = set(tokenize(f"{chunk['doc_title']} {chunk['section']} {chunk['text']}"))
    tokens: set[str] = chunk["_tokens"]
    return tokens


def keyword_score(query_tokens: set[str], tokens: set[str]) -> float:
    """Tỉ lệ từ của truy vấn có mặt trong đoạn, từ 0 đến 1."""
    return len(query_tokens & tokens) / len(query_tokens) if query_tokens else 0.0


def cosine(a: list[float], b: list[float]) -> float:
    """Độ giống nhau giữa hai vector, từ -1 đến 1."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def hybrid_search(
    query: str,
    chunks: list[dict[str, Any]],
    *,
    query_vector: list[float] | None = None,
    top_k: int = 5,
    vector_weight: float = 0.75,
    hybrid: bool = True,
) -> list[Hit]:
    """Tìm các đoạn liên quan nhất.

    Args:
        query: Truy vấn dạng văn bản.
        chunks: Danh sách đoạn (từ điển) từ chỉ mục. Mỗi đoạn có ``chunk_id``, ``doc_id``,
            ``doc_title``, ``section``, ``version``, ``effective_date``, ``category``, ``text`` và
            có thể có ``embedding``.
        query_vector: Vector nhúng của truy vấn. Bỏ trống thì chỉ dùng keyword.
        top_k: Số kết quả trả về.
        vector_weight: Trọng số của điểm vector trong chế độ hybrid (điểm keyword nhận phần còn lại).
        hybrid: True thì trộn vector với keyword. False thì chỉ dùng vector (semantic thuần).

    Returns:
        Danh sách ``Hit`` sắp giảm dần theo điểm, tối đa ``top_k``, điểm làm tròn 4 chữ số.
    """
    # TODO(LAB-3): Retrieve — chấm điểm keyword, semantic và hybrid rồi lấy top-k
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Retrieve — chấm điểm keyword, semantic và hybrid rồi lấy top-k")
