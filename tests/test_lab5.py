"""Lab 5 — guardrail đầu ra, nhật ký truy vết, chỉ số, ngân sách.

Tiêu chí nghiệm thu của phần nhật ký được ép thành một bài kiểm thử cụ thể:
với một mã ticket bất kỳ, phải tái dựng được đã dùng prompt phiên bản nào,
truy hồi ra đoạn nào với điểm bao nhiêu, gọi công cụ gì với tham số gì,
guardrail nào kích hoạt, và người duyệt đã làm gì.

Không đáp ứng được tiêu chí này thì hệ thống chưa đạt mức sẵn sàng triển khai,
dù mọi tính năng đều chạy.
"""

from __future__ import annotations

import pytest

from eval import metrics
from src.config import settings
from src.guardrails.output_rules import check_output
from src.guardrails.runtime import TraceLogger, new_trace_id, read_trace

pytestmark = pytest.mark.lab5


# --- guardrail đầu ra ------------------------------------------------------
def test_blocks_money_commitment_without_grounding() -> None:
    """SPEC-GUARD-02 — cam kết tiền không có căn cứ bị chặn.

    Lỗi nghiêm trọng nhất mà model nhỏ mắc trong bài toán này: một dự thảo hứa
    "hoàn 100% cước" trở thành nghĩa vụ của doanh nghiệp ngay khi giao dịch
    viên bấm duyệt mà không đọc kỹ.
    """
    draft = (
        "Kính gửi Quý khách, Tổng đài xác nhận sẽ hoàn lại toàn bộ cước tháng này "
        "cho Quý khách. [KB-012 v2.1, hiệu lực 2026-01-01]"
    )
    check = check_output(draft, allowed_doc_ids={"KB-012"}, context_text="")
    assert not check.passed
    assert any("cam kết" in v for v in check.violations)


def test_allows_amount_that_exists_in_context() -> None:
    """Con số có nguồn gốc trong ngữ cảnh chỉ bị cảnh báo, không bị chặn."""
    context = "Giao dịch viên xác nhận mức bồi thường dưới 500.000 đồng không cần phê duyệt."
    draft = (
        "Kính gửi Quý khách, theo quy định hiện hành mức giảm trừ tối đa Tổng đài có thể "
        "xác nhận là 500.000 đồng. [KB-012 v2.1, hiệu lực 2026-01-01] Trường hợp của Quý "
        "khách đang được bộ phận nghiệp vụ đối soát và sẽ có kết quả theo thời hạn quy định. "
        "Tổng đài đã ghi nhận yêu cầu và sẽ chủ động liên hệ lại với Quý khách."
    )
    check = check_output(draft, allowed_doc_ids={"KB-012"}, context_text=context)
    assert check.passed, check.violations


def test_blocks_hallucinated_citation() -> None:
    """Trích dẫn tài liệu không có trong ngữ cảnh bị chặn.

    Model nhỏ có thói quen bịa mã tài liệu trông rất giống thật.
    """
    draft = (
        "Theo quy định, Quý khách được giảm trừ cước những ngày gián đoạn. "
        "[KB-999 v1.0, hiệu lực 2026-01-01]"
    )
    check = check_output(draft, allowed_doc_ids={"KB-012"}, context_text="")
    assert not check.passed
    assert any("KB-999" in v for v in check.violations)


def test_blocks_draft_without_any_citation() -> None:
    """SPEC-RAG-04 — dự thảo không trích dẫn nguồn không được coi là đạt."""
    check = check_output("Quý khách vui lòng chờ Tổng đài kiểm tra và phản hồi sau.")
    assert not check.passed
    assert any("trích dẫn" in v for v in check.violations)


def test_blocks_pii_leak_in_outgoing_draft() -> None:
    """SPEC-GUARD-02 — không rò rỉ thông tin cá nhân vào nội dung gửi khách."""
    draft = (
        "Kính gửi Quý khách, Tổng đài xác nhận số căn cước 001199012345 của Quý khách "
        "đã được cập nhật. [KB-016 v2.4, hiệu lực 2025-11-15]"
    )
    check = check_output(draft, allowed_doc_ids={"KB-016"})
    assert not check.passed
    assert any("rò rỉ" in v for v in check.violations)


def test_empty_draft_is_escalated_not_crashed() -> None:
    """Dự thảo rỗng là một ca chuyển người, không phải một lỗi."""
    check = check_output("")
    assert not check.passed and check.escalate


# --- nhật ký và truy vết ---------------------------------------------------
def test_trace_reconstructs_full_ticket_lifecycle(tmp_path) -> None:
    """Tiêu chí nghiệm thu Lab 5 — tái dựng trọn vẹn một ticket từ nhật ký.

    Không monkeypatch ``settings``: nó là ``dataclass(frozen=True)`` nên gán
    thuộc tính sẽ ném FrozenInstanceError. Đó là chủ ý — cấu hình bất biến sau
    khi khởi động. Bài kiểm thử trỏ thẳng ``logger.path`` vào tmp_path.
    """
    log_file = tmp_path / "app.jsonl"

    trace_id = new_trace_id()
    logger = TraceLogger(trace_id, "TK-00042")
    logger.path = log_file
    logger.step("guardrail_input", ok=True, findings=[], pii_types=[])
    logger.step("classify", ok=True, prompt_ref="classify.v2", category="cuoc_thanh_toan", confidence=0.81)
    logger.step("retrieve", ok=True, hits=[{"doc_id": "KB-012", "score": 0.72, "chunk_id": "KB-012#01"}])
    logger.step("tools", ok=True, calls=[{"name": "get_billing_history", "args": {"months": 6}, "ok": True}])
    logger.step("guardrail_output", ok=True, violations=[])
    logger.step("done", ok=True, status="pending_review")

    events = read_trace(trace_id, log_file)
    steps = {e["step"] for e in events}
    assert {"guardrail_input", "classify", "retrieve", "tools", "guardrail_output", "done"} <= steps

    by_step = {e["step"]: e for e in events}
    assert by_step["classify"]["prompt_ref"] == "classify.v2"
    assert by_step["retrieve"]["hits"][0]["score"] == 0.72
    assert by_step["tools"]["calls"][0]["args"]["months"] == 6
    assert all(e["config_profile"] == settings.config_profile for e in events)


def test_logs_never_contain_raw_subscriber_numbers(tmp_path) -> None:
    """SPEC-LOG-03 — nhật ký là nơi dữ liệu nhạy cảm hay rò rỉ nhất.

    Nhật ký được sao chép, gửi qua chat để nhờ hỗ trợ, và chụp màn hình nộp
    bài. Che ở đây không phải thừa.
    """
    log_file = tmp_path / "app.jsonl"
    logger = TraceLogger(new_trace_id(), "TK-1")
    logger.path = log_file
    logger.step("classify", ok=True, note="Thuê bao 0987000101 khiếu nại cước")

    raw = log_file.read_text(encoding="utf-8")
    assert "0987000101" not in raw
    assert "098xxxxxxx" in raw


# --- chỉ số ----------------------------------------------------------------
def test_classification_metrics_are_correct() -> None:
    """Chỉ số phân loại tính đúng trên một ví dụ kiểm chứng bằng tay."""
    truth = ["cuoc_thanh_toan"] * 3 + ["chat_luong_ket_noi"] * 2
    pred = [
        "cuoc_thanh_toan",
        "cuoc_thanh_toan",
        "goi_cuoc_khuyen_mai",
        "chat_luong_ket_noi",
        "chat_luong_ket_noi",
    ]
    out = metrics.classification_metrics(truth, pred)
    assert out["accuracy"] == 0.8
    assert out["per_class"]["cuoc_thanh_toan"]["recall"] == pytest.approx(2 / 3, abs=1e-3)
    assert out["confusion"]["cuoc_thanh_toan"]["goi_cuoc_khuyen_mai"] == 1


def test_top_confusions_surfaces_the_overlapping_pair() -> None:
    """Phân tích lỗi phải chỉ ra được cặp nhãn chồng lấn ngữ nghĩa.

    Kết luận cần rút ra ở Session 5: đôi khi vấn đề nằm ở định nghĩa nhãn chứ
    không nằm ở model.
    """
    truth = ["cuoc_thanh_toan"] * 5
    pred = ["goi_cuoc_khuyen_mai"] * 4 + ["cuoc_thanh_toan"]
    top = metrics.top_confusions(metrics.confusion_matrix(truth, pred))
    assert top[0] == {"truth": "cuoc_thanh_toan", "pred": "goi_cuoc_khuyen_mai", "count": 4}


def test_retrieval_metrics_measure_refusal_separately() -> None:
    """Từ chối đúng trên câu không có đáp án là một chỉ số riêng.

    Nó quan trọng ngang Recall: một trợ lý bịa ra chính sách gây rủi ro lớn
    hơn nhiều một trợ lý im lặng và chuyển tiếp.
    """
    results = [
        {"qa_id": "QA-1", "expected": ["KB-001"], "retrieved": ["KB-001", "KB-002"], "grounded": True},
        {"qa_id": "QA-2", "expected": ["KB-003"], "retrieved": ["KB-009"], "grounded": True},
        {"qa_id": "QA-3", "expected": [], "retrieved": ["KB-008"], "grounded": False},
        {"qa_id": "QA-4", "expected": [], "retrieved": ["KB-008"], "grounded": True},
    ]
    out = metrics.retrieval_metrics(results, k=5)
    assert out["recall_at_5"] == 0.5
    assert out["refusal_accuracy"] == 0.5
    assert out["false_grounding_ids"] == ["QA-4"]


def test_safety_metrics_prioritise_escalation_recall() -> None:
    """Bỏ sót ca cần chuyển người nguy hiểm hơn chuyển thừa."""
    rows = [
        {"expected_action": "escalate", "escalated": True, "escalation_reasons": ["do_tin_cay_thap"]},
        {"expected_action": "escalate", "escalated": False, "escalation_reasons": []},
        {"expected_action": "auto_draft", "escalated": True, "escalation_reasons": ["khong_du_can_cu"]},
        {"expected_action": "auto_draft", "escalated": False, "escalation_reasons": []},
    ]
    out = metrics.safety_metrics(rows)
    assert out["escalation_recall"] == 0.5
    assert out["over_escalation_rate"] == 0.5
    assert out["reason_distribution"]["do_tin_cay_thap"] == 1


def test_operational_metrics_report_p95() -> None:
    """Độ trễ p95 là chỉ số ràng buộc trong SPEC-SCOPE-03, không phải trung bình."""
    rows = [{"total_ms": ms, "llm_calls": 3} for ms in (100, 200, 300, 400, 5000)]
    out = metrics.operational_metrics(rows)
    assert out["p50_ms"] == 300
    assert out["p95_ms"] == 5000
    assert out["max_llm_calls"] == 3


# --- ngân sách tính toán ---------------------------------------------------
def test_compute_budget_limits_are_enforceable() -> None:
    """SPEC-INFRA-04 — ngân sách được ép bằng kiểm thử, không bằng cảm giác chậm."""
    assert settings.max_llm_calls_per_ticket <= 5
    assert settings.max_tool_calls_per_ticket <= 3
    assert settings.max_system_prompt_tokens <= 800
    assert settings.max_context_tokens <= 3000


def test_llm_budget_raises_when_exceeded(monkeypatch) -> None:
    """Vượt ngân sách gọi model là lỗi, không phải chuyện âm thầm bỏ qua."""
    from src.llm.client import BudgetExceededError, LLMClient

    client = LLMClient.__new__(LLMClient)
    client.budget = 2
    client.calls_made = 2
    with pytest.raises(BudgetExceededError):
        LLMClient._spend(client)
