"""Sinh dự thảo phản hồi có căn cứ — SPEC-PROMPT-03.

Hai điều cần giữ chắc ở tầng này:

1. Không có căn cứ thì không sinh. Quy tắc từ chối của SPEC-RAG-03 được kiểm
   tra trước khi gọi model, không phải sau. Gọi model rồi mới lọc là lãng phí
   và vẫn để lọt trường hợp model bịa trơn tru đến mức bộ lọc không bắt được.
2. Đầu ra được đối chiếu ngược với ngữ cảnh: mọi trích dẫn trong dự thảo phải
   trỏ tới một tài liệu thực sự có trong danh sách đã truy hồi. Model nhỏ có
   thói quen bịa mã tài liệu trông rất giống thật.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.agent.loader import load_prompt
from src.knowledge.retriever import RetrievalResult
from src.llm.client import LLMClient, get_client

SYSTEM = (
    "Bạn soạn dự thảo phản hồi cho giao dịch viên chăm sóc khách hàng viễn thông. "
    "Bạn chỉ dùng thông tin có trong ngữ cảnh được cung cấp."
)

INSUFFICIENT = "KHÔNG ĐỦ CĂN CỨ"

_CITATION = re.compile(r"\[(KB-\d{3})\s+v([\d.]+),\s*hiệu lực\s*(\d{4}-\d{2}-\d{2})\]")


@dataclass
class Draft:
    """Dự thảo phản hồi kèm mọi thứ cần để người duyệt ra quyết định."""

    text: str
    grounded: bool
    citations: list[str] = field(default_factory=list)
    invalid_citations: list[str] = field(default_factory=list)
    prompt_ref: str = ""
    reason: str = ""

    @property
    def has_valid_citation(self) -> bool:
        """True nếu có ít nhất một trích dẫn và không có trích dẫn bịa."""
        return bool(self.citations) and not self.invalid_citations

    def to_dict(self) -> dict[str, Any]:
        """Dạng từ điển để ghi nhật ký và trả qua API."""
        return {
            "text": self.text,
            "grounded": self.grounded,
            "citations": self.citations,
            "invalid_citations": self.invalid_citations,
            "prompt_ref": self.prompt_ref,
            "reason": self.reason,
        }


def check_citations(text: str, retrieval: RetrievalResult) -> tuple[list[str], list[str]]:
    """Đối chiếu trích dẫn trong dự thảo với các đoạn đã truy hồi.

    Returns:
        Cặp (trích dẫn hợp lệ, trích dẫn không tìm thấy trong ngữ cảnh).
    """
    available = {hit.doc_id for hit in retrieval.hits}
    found: list[str] = []
    invalid: list[str] = []
    for match in _CITATION.finditer(text):
        doc_id = match.group(1)
        (found if doc_id in available else invalid).append(doc_id)
    return sorted(set(found)), sorted(set(invalid))


def generate_reply(
    ticket_text: str,
    classification: dict[str, Any],
    retrieval: RetrievalResult,
    tool_results: str,
    *,
    client: LLMClient | None = None,
) -> Draft:
    """Soạn dự thảo phản hồi cho một ticket.

    Args:
        ticket_text: Nội dung ticket gốc.
        classification: Kết quả phân loại dạng từ điển.
        retrieval: Kết quả truy hồi, gồm cả cờ ``grounded``.
        tool_results: Khối văn bản kết quả gọi công cụ.
        client: Client dùng để gọi model.

    Returns:
        ``Draft``. Khi không đủ căn cứ, trả về dự thảo rỗng có ``grounded=False``
        và KHÔNG gọi model — đây là ranh giới an toàn quan trọng nhất của hệ thống.
    """
    # TODO(LAB-4): Không đủ căn cứ thì KHÔNG gọi model — kiểm tra TRƯỚC, không phải sau
    #   Chạy "uv run pytest -m lab4" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-4: Không đủ căn cứ thì KHÔNG gọi model — kiểm tra TRƯỚC, không phải sau")


def _fmt_classification(c: dict[str, Any]) -> str:
    return (
        f"nhóm={c.get('category')} · ưu tiên={c.get('priority')} · "
        f"sắc thái={c.get('sentiment')} · độ tin cậy={c.get('confidence')}"
    )
