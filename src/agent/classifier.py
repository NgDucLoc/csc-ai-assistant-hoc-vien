"""Phân loại và trích xuất thực thể từ ticket — năng lực AI đầu tiên của hệ thống.

Một prompt chỉ làm một nhiệm vụ (SPEC-PROMPT-01). Việc gộp phân loại với soạn
phản hồi vào cùng một lời gọi làm suy giảm chất lượng rõ rệt với model nhỏ, và
quan trọng hơn, làm mất khả năng đo riêng từng bước ở Session 5 — lúc đó
không ai biết ma trận nhầm lẫn xấu là do phân loại kém hay do sinh văn bản kém.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.agent.loader import load_prompt
from src.llm.client import LLMClient, get_client
from src.llm.schema import (
    CLASSIFICATION_FALLBACK,
    CLASSIFICATION_SCHEMA,
    ParseOutcome,
    parse_with_retry,
    schema_hint,
)

SYSTEM = (
    "Bạn là bộ phân loại ticket chăm sóc khách hàng viễn thông. "
    "Bạn chỉ trả về JSON hợp lệ, không kèm lời dẫn, không kèm khối mã."
)


@dataclass
class Classification:
    """Kết quả phân loại một ticket."""

    category: str
    priority: str
    sentiment: str
    confidence: float
    entities: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    needs_human: bool = False
    prompt_ref: str = ""
    attempts: int = 1
    defense_layer: str = "direct"
    from_cache: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Dạng từ điển để ghi nhật ký và trả qua API."""
        return {
            "category": self.category,
            "priority": self.priority,
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "entities": self.entities,
            "reason": self.reason,
            "needs_human": self.needs_human,
            "prompt_ref": self.prompt_ref,
            "attempts": self.attempts,
            "defense_layer": self.defense_layer,
        }


def classify(
    ticket_text: str,
    *,
    client: LLMClient | None = None,
    prompt_version: int | None = None,
) -> Classification:
    """Phân loại một ticket, đi qua đủ bốn lớp phòng vệ đầu ra.

    Args:
        ticket_text: Nội dung thô của ticket.
        client: Client dùng để gọi model. Bỏ trống thì dùng client chung.
        prompt_version: Ép một phiên bản prompt cụ thể. Dùng khi so sánh v1 và v2.

    Returns:
        ``Classification``. Không bao giờ ném lỗi vì đầu ra hỏng — lớp phòng vệ
        thứ tư biến trường hợp đó thành một ca chuyển người.
    """
    # TODO(LAB-3): Gọi model qua bốn lớp phòng vệ; không bao giờ ném lỗi ra ngoài
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Gọi model qua bốn lớp phòng vệ; không bao giờ ném lỗi ra ngoài")


def rewrite_query(ticket_text: str, category: str, *, client: LLMClient | None = None) -> str | None:
    """Viết lại lời phàn nàn thành truy vấn tra cứu chính sách.

    Đây là một trong hai cải tiến truy hồi mà Session 3 bước 4 yêu cầu đo. Trả
    về None khi model không phản hồi được, để bên gọi rơi về truy vấn gốc thay
    vì dừng cả quy trình.
    """
    client = client or get_client()
    prompt = load_prompt("rewrite_query")
    try:
        resp = client.complete(
            task="rewrite_query",
            system="Bạn viết lại truy vấn tra cứu. Chỉ trả về một dòng.",
            user=prompt.render(ticket_text=ticket_text, category=category),
        )
    except Exception:  # noqa: BLE001 — suy giảm có kiểm soát, SPEC-ARCH-02
        return None
    line = resp.text.strip().splitlines()[0] if resp.text.strip() else ""
    return line.strip().strip('"') or None
