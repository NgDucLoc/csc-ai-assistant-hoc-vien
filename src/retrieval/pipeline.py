"""Retrieval Pipeline — ghép pha runtime của RAG (slide 39) thành một ``Retriever``.

Thứ tự các bước, mỗi bước là một module:

    truy vấn → Query Transformation (transform) → Retrieve (search) → Filter (filters)
             → Rerank (rerank) → Judge (filters.judge_evidence) → Context (context.assemble)

Retriever đọc chỉ mục JSON. Chưa có chỉ mục thì dựng chỉ mục từ khóa ngay trong bộ nhớ từ
``data/knowledge/``: đường lùi này giữ cho bộ kiểm thử chạy được trên máy chưa có máy chủ embedding
và trên runner CI không có GPU.

Chỉ mục có vector và ``RETRIEVE_MODE=auto``: Retriever nhúng truy vấn bằng model embedding và chạy
hybrid. Model embedding không phản hồi thì rơi về keyword và ghi rõ ở ``RetrievalResult.mode``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import settings
from src.knowledge.indexing import find_index, read_index
from src.knowledge.preparation import build_chunks
from src.retrieval.filters import filter_hits, judge_evidence
from src.retrieval.models import Hit, RetrievalResult
from src.retrieval.rerank import rerank
from src.retrieval.search import chunk_tokens, hybrid_search


class Retriever:
    """Truy hồi từ chỉ mục JSON, có tùy chọn kết hợp tìm kiếm từ khóa với vector."""

    def __init__(self, index_path: str | Path | None = None, *, client: Any = None) -> None:
        """Nạp chỉ mục.

        Args:
            index_path: Thư mục hoặc tệp ``index.json``. Mặc định thử chỉ mục tự dựng trước, rồi tới
                bản dựng sẵn ở ``data/index_prebuilt/``.
            client: Đối tượng có ``embed(texts)``. Bỏ trống thì dùng ``LLMClient`` dùng chung.
        """
        self.path = find_index(index_path)
        if self.path is None:
            self.embed_model = "(chưa nhúng — chỉ tìm kiếm từ khóa)"
            self.built_profile = "-"
            self.chunks = self._chunks_in_memory()
        else:
            payload = read_index(self.path)
            self.embed_model = payload.get("embed_model", "?")
            self.built_profile = payload.get("config_profile", "?")
            self.chunks = payload["chunks"]
        for c in self.chunks:
            chunk_tokens(c)
        self.has_vectors = any(c.get("embedding") for c in self.chunks)
        self._client = client
        self._embed_failed = False

    @staticmethod
    def _chunks_in_memory() -> list[dict[str, Any]]:
        return [
            {
                "chunk_id": c.chunk_id,
                "doc_id": c.doc_id,
                "doc_title": c.doc_title,
                "section": c.section,
                "category": c.category,
                "version": c.version,
                "effective_date": c.effective_date,
                "text": c.text,
                "embedding": [],
            }
            for c in build_chunks()
        ]

    def query_vector(self, text: str) -> list[float] | None:
        """Nhúng truy vấn nếu chế độ cho phép. Trả về None khi phải rơi về keyword."""
        if not self.has_vectors or settings.retrieve_mode == "keyword" or self._embed_failed:
            return None
        if settings.cache_mode == "cache_only":  # chế độ cấm gọi model
            return None
        try:
            from src.llm.client import get_client

            client = self._client or get_client()
            return list(client.embed([text])[0])
        except Exception:  # noqa: BLE001 — model embedding không phản hồi: suy giảm về keyword
            self._embed_failed = True
            return None

    def search(
        self,
        query: str,
        *,
        top_k: int | None = None,
        query_vector: list[float] | None = None,
        hybrid: bool = True,
    ) -> list[Hit]:
        """Tìm các đoạn liên quan nhất (bước Retrieve)."""
        return hybrid_search(
            query,
            self.chunks,
            query_vector=query_vector,
            top_k=top_k or settings.retrieve_top_k,
            vector_weight=settings.vector_weight,
            hybrid=hybrid,
        )

    def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
        query_vector: list[float] | None = None,
        min_score: float | None = None,
        rewritten: str | None = None,
        categories: set[str] | None = None,
        as_of: str | None = None,
    ) -> RetrievalResult:
        """Truy hồi và quyết định có đủ căn cứ để sinh phản hồi hay không (SPEC-RAG-02, SPEC-RAG-03)."""
        min_score = settings.retrieve_min_score if min_score is None else min_score
        text = rewritten or query
        vector = query_vector if query_vector is not None else self.query_vector(text)

        hits = self.search(text, top_k=top_k, query_vector=vector)
        hits = filter_hits(hits, categories=categories, as_of=as_of)
        if settings.rerank_enabled:
            hits = rerank(hits, text)
        grounded, reason = judge_evidence(hits, min_score)
        return RetrievalResult(
            query, rewritten, hits, grounded, reason, mode="hybrid" if vector is not None else "keyword"
        )


_default: Retriever | None = None


def get_retriever() -> Retriever:
    """Trả về retriever dùng chung của tiến trình."""
    global _default
    if _default is None:
        _default = Retriever()
    return _default
