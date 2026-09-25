"""Quy trình xử lý một ticket từ đầu tới dự thảo chờ duyệt — SPEC-FLOW-01…04.

Nguyên tắc bất biến của toàn hệ thống (SPEC-FLOW-03):

    KHÔNG có đường dẫn nào cho phép phản hồi tới khách hàng mà chưa qua thao
    tác duyệt của con người, kể cả trong bản demo cuối khóa.

Trạng thái cuối mà quy trình này sinh ra luôn là ``PENDING_REVIEW`` hoặc
``ESCALATED``. Không có nhánh nào đi tới ``SENT``. Việc chuyển sang ``SENT``
chỉ xảy ra ở ``review.approve()``, và ``tests/test_lab4.py`` có một bài kiểm
thử quét đồ thị trạng thái để ép ràng buộc đó.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from src.agent.classifier import Classification, classify
from src.agent.generator import Draft, generate_reply
from src.agent.tools import ToolRunner, rule_based_plan
from src.config import settings
from src.guardrails.input_rules import check_input
from src.guardrails.output_rules import check_output
from src.guardrails.runtime import TraceLogger, new_trace_id
from src.llm.cache import CacheMissError
from src.llm.client import BudgetExceededError, CircuitOpenError, LLMClient, get_client
from src.retrieval.models import RetrievalResult
from src.retrieval.pipeline import Retriever, get_retriever
from src.retrieval.transform import rewrite_query

CONFIDENCE_THRESHOLD = 0.60


class Status(StrEnum):
    """Trạng thái của một ticket trong hệ thống."""

    PENDING_REVIEW = "pending_review"
    ESCALATED = "escalated"
    APPROVED = "approved"
    EDITED_APPROVED = "edited_approved"
    REJECTED = "rejected"
    SENT = "sent"


# Chỉ hai trạng thái này được sinh ra bởi quy trình tự động.
AUTOMATED_TERMINAL_STATES = frozenset({Status.PENDING_REVIEW, Status.ESCALATED})


class EscalationReason(StrEnum):
    """Các điều kiện bắt buộc chuyển người — SPEC-FLOW-02.

    Bốn điều kiện đầu là mức tối thiểu mà mọi nhóm phải cài đặt. Ba điều kiện
    sau là phần mở rộng của bản giải mẫu.
    """

    LOW_CONFIDENCE = "do_tin_cay_thap"
    NO_GROUNDING = "khong_du_can_cu"
    MONEY_DISPUTE = "tranh_chap_tien"
    TOP_PRIORITY = "muc_uu_tien_cao_nhat"
    GUARDRAIL_INPUT = "guardrail_dau_vao"
    GUARDRAIL_OUTPUT = "guardrail_dau_ra"
    SYSTEM_DEGRADED = "he_thong_suy_giam"


@dataclass
class TicketResult:
    """Kết quả xử lý một ticket, đủ để hiển thị trên màn hình duyệt."""

    ticket_id: str
    trace_id: str
    status: Status
    classification: dict[str, Any]
    retrieval: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]
    draft: dict[str, Any]
    escalation_reasons: list[str] = field(default_factory=list)
    guardrails: dict[str, Any] = field(default_factory=dict)
    config_profile: str = settings.config_profile
    llm_calls: int = 0
    total_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Dạng từ điển để trả qua API và lưu vào cơ sở dữ liệu."""
        data = asdict(self)
        data["status"] = self.status.value
        return data


def _money_dispute(text: str, classification: Classification) -> bool:
    keywords = ("bồi thường", "hoàn tiền", "trả lại tiền", "đền bù", "khiếu nại số tiền")
    low = text.lower()
    return any(k in low for k in keywords) or (
        classification.category == "cuoc_thanh_toan" and bool(classification.entities.get("amount"))
    )


def process_ticket(
    ticket_id: str,
    ticket_text: str,
    *,
    client: LLMClient | None = None,
    retriever: Retriever | None = None,
    prompt_version: int | None = None,
) -> TicketResult:
    """Chạy toàn bộ quy trình cho một ticket.

    Luồng: guardrail đầu vào → phân loại → quyết định rẽ nhánh → truy hồi →
    gọi công cụ → sinh dự thảo → guardrail đầu ra → chờ duyệt.

    Mọi lỗi ở từng mắt xích đều được bắt và chuyển thành một ca chuyển người.
    Hệ thống suy giảm có kiểm soát, không dừng đột ngột (SPEC-ARCH-02 mục 3).

    Args:
        ticket_id: Mã ticket, dùng làm khóa trong nhật ký.
        ticket_text: Nội dung thô do khách hàng gửi.
        client: Client model. Bỏ trống thì dùng client chung.
        retriever: Bộ truy hồi. Bỏ trống thì dùng bộ chung.
        prompt_version: Ép phiên bản prompt phân loại, dùng khi so sánh A/B.

    Returns:
        ``TicketResult`` với trạng thái luôn thuộc ``AUTOMATED_TERMINAL_STATES``.
    """
    # TODO(LAB-4): Ghép quy trình và đặt tối thiểu 4 điều kiện chuyển người
    #   Chạy "uv run pytest -m lab4" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-4: Ghép quy trình và đặt tối thiểu 4 điều kiện chuyển người")


def _escalate(
    ticket_id: str,
    trace_id: str,
    logger: TraceLogger,
    reasons: list[str],
    *,
    guardrails: dict[str, Any],
    note: str,
    llm_calls: int,
) -> TicketResult:
    """Dựng kết quả cho một ca chuyển người sớm."""
    logger.step("done", ok=True, status=Status.ESCALATED.value, reasons=reasons, note=note)
    return TicketResult(
        ticket_id=ticket_id,
        trace_id=trace_id,
        status=Status.ESCALATED,
        classification={},
        retrieval=[],
        tool_calls=[],
        draft={"text": "", "grounded": False, "reason": note},
        escalation_reasons=sorted(set(reasons)),
        guardrails=guardrails,
        llm_calls=llm_calls,
        total_ms=logger.summary()["total_ms"],
    )
