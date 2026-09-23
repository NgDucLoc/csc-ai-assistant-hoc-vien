"""Truy hồi tri thức có ngưỡng, có trích dẫn, và biết nói không đủ căn cứ.

Ba quy định của SPEC-RAG được cài đặt ở đây:

* **SPEC-RAG-02** — trả về top-k kèm điểm tương đồng, có tùy chọn viết lại
  truy vấn trước khi tìm.
* **SPEC-RAG-03** — nếu điểm cao nhất dưới ngưỡng, hệ thống KHÔNG sinh phản
  hồi mà chuyển người. Với bài toán chăm sóc khách hàng, một trợ lý bịa ra
  chính sách gây rủi ro nghiệp vụ nghiêm trọng hơn nhiều so với một trợ lý im
  lặng và chuyển tiếp cho người xử lý.
* **SPEC-RAG-04** — mỗi đoạn trả về mang đủ ``doc_id``, ``version`` và
  ``effective_date`` để câu trả lời truy ngược được về tài liệu gốc.

Bộ dữ liệu cố ý chứa 5 câu hỏi không có đáp án trong kho. Nhóm nào bỏ qua
ngưỡng ở đây sẽ thấy hệ thống bịa ra chính sách cho đúng 5 câu đó.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import settings

_WORD = re.compile(r"[0-9a-zA-ZÀ-ỹ]+", re.UNICODE)


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

    @property
    def top_score(self) -> float:
        """Điểm cao nhất, 0.0 nếu không có kết quả nào."""
        return self.hits[0].score if self.hits else 0.0

    def context_block(self, max_chars: int = 2000) -> str:
        """Ghép các đoạn thành khối ngữ cảnh để chèn vào prompt sinh phản hồi."""
        parts: list[str] = []
        used = 0
        for hit in self.hits:
            block = f"{hit.citation()} {hit.doc_title} — {hit.section}\n{hit.text}"
            if used + len(block) > max_chars:
                break
            parts.append(block)
            used += len(block)
        return "\n\n".join(parts)


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _WORD.findall(text)]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class Retriever:
    """Truy hồi từ chỉ mục JSON, có tùy chọn kết hợp tìm kiếm từ khóa.

    Chỉ mục JSON được chọn làm định dạng chính thay vì phụ thuộc cứng vào
    Chroma, vì nó commit được vào repo và nhờ đó ``data/index_prebuilt/`` chạy
    ngay trên máy học viên mà không cần dựng lại — đúng yêu cầu dự phòng của
    Session 3.
    """

    def __init__(self, index_path: str | Path | None = None) -> None:
        """Nạp chỉ mục.

        Args:
            index_path: Thư mục chứa ``index.json``. Mặc định thử chỉ mục tự
                dựng trước, rồi mới tới bản dựng sẵn.

        Khi chưa có tệp chỉ mục nào, retriever dựng chỉ mục từ khóa ngay trong
        bộ nhớ từ ``data/knowledge/``. Đường lùi này không phải để tiết kiệm:
        nó là thứ giữ cho Lab 3 và toàn bộ bộ kiểm thử chạy được trên máy chưa
        có máy chủ embedding, và trên runner CI không có GPU.
        """
        self.path = self._resolve(index_path)
        if self.path is None:
            self.embed_model = "(chưa nhúng — chỉ tìm kiếm từ khóa)"
            self.built_profile = "-"
            self.chunks = self._chunks_in_memory()
        else:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            self.embed_model = payload.get("embed_model", "?")
            self.built_profile = payload.get("config_profile", "?")
            self.chunks = payload["chunks"]
        for c in self.chunks:
            c["_tokens"] = set(_tokens(f"{c['doc_title']} {c['section']} {c['text']}"))

    @staticmethod
    def _chunks_in_memory() -> list[dict[str, Any]]:
        from src.knowledge.indexer import build_chunks

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

    @staticmethod
    def _resolve(index_path: str | Path | None) -> Path | None:
        candidates = (
            [Path(index_path)]
            if index_path
            else [
                settings.abs_path(settings.chroma_path),
                settings.abs_path("data/index_prebuilt"),
            ]
        )
        for cand in candidates:
            f = cand / "index.json" if cand.is_dir() else cand
            if f.exists():
                return f
        return None

    # -- tìm kiếm ----------------------------------------------------------
    def search(
        self,
        query: str,
        *,
        top_k: int | None = None,
        query_vector: list[float] | None = None,
        hybrid: bool = True,
    ) -> list[Hit]:
        """Tìm các đoạn liên quan nhất.

        Args:
            query: Truy vấn dạng văn bản.
            top_k: Số kết quả trả về. Mặc định lấy từ cấu hình.
            query_vector: Vector nhúng của truy vấn. Nếu bỏ trống, chỉ dùng
                tìm kiếm từ khóa — đủ để Lab 3 chạy khi chưa có máy chủ embedding.
            hybrid: Kết hợp điểm vector với điểm từ khóa. Với tiếng Việt và tài
                liệu nhiều mã gói cước, tìm kiếm từ khóa bắt được nhiều trường
                hợp mà vector bỏ sót.

        Returns:
            Danh sách ``Hit`` sắp giảm dần theo điểm.
        """
        top_k = top_k or settings.retrieve_top_k
        q_tokens = set(_tokens(query))

        scored: list[tuple[float, dict[str, Any]]] = []
        for chunk in self.chunks:
            lexical = len(q_tokens & chunk["_tokens"]) / len(q_tokens) if q_tokens else 0.0
            if query_vector is not None and chunk.get("embedding"):
                vector = _cosine(query_vector, chunk["embedding"])
                score = 0.75 * vector + 0.25 * lexical if hybrid else vector
            else:
                score = lexical
            scored.append((score, chunk))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            Hit(
                chunk_id=c["chunk_id"],
                doc_id=c["doc_id"],
                doc_title=c["doc_title"],
                section=c["section"],
                version=c["version"],
                effective_date=c["effective_date"],
                text=c["text"],
                score=round(s, 4),
            )
            for s, c in scored[:top_k]
        ]

    def retrieve(
        self,
        query: str,
        *,
        top_k: int | None = None,
        query_vector: list[float] | None = None,
        min_score: float | None = None,
        rewritten: str | None = None,
    ) -> RetrievalResult:
        """Truy hồi và quyết định có đủ căn cứ để sinh phản hồi hay không.

        Đây là nơi cài đặt SPEC-RAG-03. Ranh giới an toàn quan trọng nhất của
        toàn hệ thống nằm ở đúng ba dòng so sánh dưới đây.
        """
        # TODO(LAB-3): SPEC-RAG-03 — điểm dưới ngưỡng thì KHÔNG đủ căn cứ, chuyển người
        #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
        raise NotImplementedError("LAB-3: SPEC-RAG-03 — điểm dưới ngưỡng thì KHÔNG đủ căn cứ, chuyển người")


_default: Retriever | None = None


def get_retriever() -> Retriever:
    """Trả về retriever dùng chung của tiến trình."""
    global _default
    if _default is None:
        _default = Retriever()
    return _default
