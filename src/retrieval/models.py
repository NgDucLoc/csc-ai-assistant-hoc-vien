"""Kiểu dữ liệu của pha truy hồi: một kết quả tìm được và một lần truy hồi trọn vẹn."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Hit:
    """Một đoạn tri thức truy hồi được, kèm điểm và siêu dữ liệu trích dẫn."""

    chunk_id: str
    doc_id: str
    doc_title: str
    section: str
    version: str
    effective_date: str
    text: str
    score: float
    category: str = ""

    def citation(self) -> str:
        """Chuỗi trích dẫn chuẩn — SPEC-RAG-04."""
        return f"[{self.doc_id} v{self.version}, hiệu lực {self.effective_date}]"


@dataclass
class RetrievalResult:
    """Kết quả một lần truy hồi, gồm cả quyết định có đủ căn cứ hay không."""

    query: str
    rewritten_query: str | None
    hits: list[Hit]
    grounded: bool
    reason: str
    mode: str = "keyword"

    @property
    def top_score(self) -> float:
        """Điểm cao nhất, 0.0 nếu không có kết quả nào."""
        return self.hits[0].score if self.hits else 0.0

    def context_block(self, max_chars: int = 2000) -> str:
        """Ghép các đoạn thành khối ngữ cảnh để chèn vào prompt sinh phản hồi."""
        from src.context.assemble import assemble_context

        return assemble_context(self.hits, max_chars)
