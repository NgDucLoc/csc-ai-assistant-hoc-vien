"""Ba công cụ giả lập và đường dự phòng theo luật — SPEC-TOOL-01…03.

Không công cụ nào kết nối hệ thống thật. Tất cả đều chỉ đọc, có timeout, và có
giới hạn số lần gọi trên một ticket.

Điểm quan trọng về mặt sư phạm nằm ở ``rule_based_plan``: model 3 tỉ tham số
gọi công cụ không ổn định — có lúc quên gọi, có lúc gọi sai tham số, có lúc
bịa ra tên công cụ không tồn tại. Đường dự phòng theo luật ở đây **là một
nguyên tắc thiết kế, không phải sự thỏa hiệp kỹ thuật**. Mọi quyết định do
model đưa ra trong hệ thống production đều cần một đường lùi tất định.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from src.config import ROOT, settings

FIXTURES = ROOT / "data" / "fixtures"


class ToolError(RuntimeError):
    """Công cụ thực thi thất bại."""


@dataclass
class ToolCall:
    """Một lần gọi công cụ, đủ chi tiết để tái dựng ở phần truy vết."""

    name: str
    args: dict[str, Any]
    ok: bool
    result: dict[str, Any] | None
    error: str | None
    latency_ms: int
    source: str  # "model" hoặc "rule"

    def to_dict(self) -> dict[str, Any]:
        """Dạng từ điển để ghi nhật ký."""
        return {
            "name": self.name,
            "args": self.args,
            "ok": self.ok,
            "result": self.result,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "source": self.source,
        }


# --- lược đồ công cụ, gửi cho model ---------------------------------------
TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "get_subscriber_info",
        "description": "Lấy gói cước hiện tại, ngày kích hoạt và trạng thái của một thuê bao.",
        "parameters": {
            "type": "object",
            "properties": {"subscriber_id": {"type": "string", "pattern": r"^0\d{9}$"}},
            "required": ["subscriber_id"],
        },
    },
    {
        "name": "get_billing_history",
        "description": "Lấy lịch sử cước của thuê bao trong N tháng gần nhất, tối đa 6 tháng.",
        "parameters": {
            "type": "object",
            "properties": {
                "subscriber_id": {"type": "string", "pattern": r"^0\d{9}$"},
                "months": {"type": "integer", "minimum": 1, "maximum": 6},
            },
            "required": ["subscriber_id"],
        },
    },
    {
        "name": "check_area_incident",
        "description": "Kiểm tra có sự cố hạ tầng tại một khu vực vào một ngày hay không.",
        "parameters": {
            "type": "object",
            "properties": {
                "area_code": {"type": "string"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["area_code"],
        },
    },
]


def _load_fixture(name: str) -> dict[str, Any]:
    path = FIXTURES / f"{name}.json"
    if not path.exists():
        raise ToolError(f"Thiếu dữ liệu giả lập {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


# --- cài đặt công cụ -------------------------------------------------------
def get_subscriber_info(subscriber_id: str) -> dict[str, Any]:
    """Trả về thông tin thuê bao từ dữ liệu giả lập."""
    data = _load_fixture("subscribers")
    if subscriber_id not in data:
        raise ToolError(f"Không tìm thấy thuê bao {subscriber_id} trong hệ thống")
    return data[subscriber_id]


def get_billing_history(subscriber_id: str, months: int = 6) -> dict[str, Any]:
    """Trả về lịch sử cước tối đa 6 tháng gần nhất."""
    months = max(1, min(int(months), 6))
    data = _load_fixture("billing")
    if subscriber_id not in data:
        raise ToolError(f"Không có lịch sử cước cho thuê bao {subscriber_id}")
    rows = data[subscriber_id][-months:]
    total = sum(r["amount"] for r in rows)
    return {"subscriber_id": subscriber_id, "months": months, "records": rows, "total": total}


def check_area_incident(area_code: str, date: str | None = None) -> dict[str, Any]:
    """Kiểm tra sự cố hạ tầng theo khu vực và ngày."""
    data = _load_fixture("incidents")
    for row in data.get(area_code.upper(), []):
        if date is None or row["from"] <= date <= row["to"]:
            return {"area_code": area_code.upper(), "has_incident": True, **row}
    return {"area_code": area_code.upper(), "has_incident": False, "date": date}


REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "get_subscriber_info": get_subscriber_info,
    "get_billing_history": get_billing_history,
    "check_area_incident": check_area_incident,
}


# --- xác thực tham số ------------------------------------------------------
def validate_args(name: str, args: dict[str, Any]) -> list[str]:
    """Kiểm tra tham số theo lược đồ TRƯỚC khi thực thi — SPEC-TOOL-02 mục 4.

    Model nhỏ hay gọi ``get_billing_history`` với ``months: "sáu"`` hoặc bỏ
    trống ``subscriber_id``. Chặn ở đây rẻ hơn nhiều so với để công cụ ném lỗi
    và phải suy ra nguyên nhân từ vết ngăn xếp.
    """
    # TODO(LAB-4): SPEC-TOOL-02 — xác thực tham số TRƯỚC khi thực thi công cụ
    #   Chạy "uv run pytest -m lab4" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-4: SPEC-TOOL-02 — xác thực tham số TRƯỚC khi thực thi công cụ")


@dataclass
class ToolRunner:
    """Thực thi công cụ trong giới hạn của SPEC-TOOL-02."""

    max_calls: int = field(default_factory=lambda: settings.max_tool_calls_per_ticket)
    calls: list[ToolCall] = field(default_factory=list)

    @property
    def budget_left(self) -> int:
        """Số lần gọi còn lại cho ticket hiện tại."""
        return max(0, self.max_calls - len(self.calls))

    def run(self, name: str, args: dict[str, Any], *, source: str = "model") -> ToolCall:
        """Gọi một công cụ và ghi lại kết quả.

        Công cụ lỗi KHÔNG làm dừng quy trình. Theo SPEC-TOOL-02 mục 5, lỗi được
        ghi nhật ký và workflow đi tiếp với ghi chú thiếu dữ liệu.
        """
        started = time.perf_counter()

        def record(ok: bool, result: dict[str, Any] | None, error: str | None) -> ToolCall:
            call = ToolCall(
                name=name,
                args=args,
                ok=ok,
                result=result,
                error=error,
                latency_ms=int((time.perf_counter() - started) * 1000),
                source=source,
            )
            self.calls.append(call)
            return call

        if self.budget_left == 0:
            return record(False, None, f"Đã dùng hết {self.max_calls} lần gọi công cụ (SPEC-TOOL-02)")

        problems = validate_args(name, args)
        if problems:
            return record(False, None, "Tham số không hợp lệ: " + "; ".join(problems))

        fn = REGISTRY.get(name)
        if fn is None:
            return record(False, None, f"Công cụ '{name}' không tồn tại")

        try:
            result = fn(**args)
        except ToolError as exc:
            return record(False, None, str(exc))
        except Exception as exc:  # noqa: BLE001 — công cụ hỏng không được làm sập hệ thống
            return record(False, None, f"Lỗi không lường trước: {exc}")

        elapsed = time.perf_counter() - started
        if elapsed > settings.tool_timeout:
            return record(False, None, f"Quá thời gian chờ {settings.tool_timeout}s")
        return record(True, result, None)

    def results_block(self) -> str:
        """Ghép kết quả công cụ thành khối văn bản chèn vào prompt sinh phản hồi."""
        if not self.calls:
            return "(không gọi công cụ nào)"
        parts: list[str] = []
        for call in self.calls:
            if call.ok:
                parts.append(f"{call.name}: {json.dumps(call.result, ensure_ascii=False)}")
            else:
                parts.append(f"{call.name}: KHÔNG LẤY ĐƯỢC DỮ LIỆU ({call.error})")
        return "\n".join(parts)


# --- đường dự phòng theo luật — SPEC-TOOL-03 ------------------------------
def rule_based_plan(category: str, entities: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Suy ra danh sách công cụ cần gọi mà không cần hỏi model.

    Bảng luật lấy nguyên từ SPEC-TOOL-03. Đây là đường chạy được kích hoạt khi
    model không gọi công cụ, gọi sai tên, hoặc trả về tham số không qua được
    khâu xác thực.

    Args:
        category: Nhóm vấn đề đã phân loại.
        entities: Thực thể trích xuất được từ ticket.

    Returns:
        Danh sách cặp (tên công cụ, tham số), theo đúng thứ tự nên gọi.
    """
    # TODO(LAB-4): SPEC-TOOL-03 — đường dự phòng theo luật khi model gọi công cụ sai
    #   Chạy "uv run pytest -m lab4" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-4: SPEC-TOOL-03 — đường dự phòng theo luật khi model gọi công cụ sai")


def _looks_like_subscriber(value: str) -> bool:
    digits = value.replace(" ", "").replace("-", "")
    return len(digits) == 10 and digits.startswith("0") and digits.isdigit()
