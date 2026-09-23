"""Guardrail vận hành và nhật ký có cấu trúc — SPEC-GUARD-03, SPEC-LOG-01…03.

Tiêu chí nghiệm thu của phần này rất cụ thể (Session 5): với một mã ticket bất
kỳ, phải tái dựng được đã dùng prompt phiên bản nào, truy hồi ra những đoạn nào
với điểm bao nhiêu, gọi công cụ gì với tham số gì, guardrail nào kích hoạt, và
người duyệt đã làm gì. Không đáp ứng được thì hệ thống chưa đạt mức sẵn sàng
triển khai — dù mọi tính năng đều chạy.

Vì vậy ``trace_id`` được sinh một lần ở biên hệ thống và đi kèm mọi bản ghi.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.config import settings
from src.guardrails.input_rules import mask_subscriber

_lock = threading.Lock()


def new_trace_id() -> str:
    """Sinh mã truy vết mới cho một ticket."""
    return f"tr-{uuid.uuid4().hex[:12]}"


@dataclass
class StepLog:
    """Nhật ký một bước trong quy trình xử lý."""

    step: str
    ok: bool
    duration_ms: int
    detail: dict[str, Any] = field(default_factory=dict)


class TraceLogger:
    """Ghi nhật ký có cấu trúc cho một ticket, mỗi dòng một sự kiện JSON."""

    def __init__(self, trace_id: str, ticket_id: str) -> None:
        """Mở phiên ghi nhật ký cho một ticket."""
        self.trace_id = trace_id
        self.ticket_id = ticket_id
        self.steps: list[StepLog] = []
        self.path = settings.abs_path(settings.log_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._started = time.perf_counter()

    def step(self, name: str, *, ok: bool = True, **detail: Any) -> None:
        """Ghi một bước xử lý.

        Mọi giá trị đi qua đây được che số thuê bao trước khi ghi ra đĩa
        (SPEC-LOG-03). Nhật ký là nơi dữ liệu nhạy cảm hay rò rỉ nhất, vì nó
        được sao chép, gửi qua chat để nhờ hỗ trợ, và chụp màn hình nộp bài.
        """
        # TODO(LAB-5): SPEC-LOG-03 — ghi nhật ký có cấu trúc, che PII trước khi ghi ra đĩa
        #   Chạy "uv run pytest -m lab5" để biết mình đã đúng chưa.
        raise NotImplementedError("LAB-5: SPEC-LOG-03 — ghi nhật ký có cấu trúc, che PII trước khi ghi ra đĩa")

    def _write(self, payload: dict[str, Any]) -> None:
        line = json.dumps(payload, ensure_ascii=False, default=str)
        with _lock, self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def summary(self) -> dict[str, Any]:
        """Tóm tắt toàn bộ vòng đời xử lý, dùng cho phần truy vết."""
        return {
            "trace_id": self.trace_id,
            "ticket_id": self.ticket_id,
            "config_profile": settings.config_profile,
            "total_ms": int((time.perf_counter() - self._started) * 1000),
            "steps": [
                {"step": s.step, "ok": s.ok, "elapsed_ms": s.duration_ms, **s.detail} for s in self.steps
            ],
        }


def _sanitize(value: Any) -> Any:
    """Che số thuê bao ở mọi tầng của cấu trúc dữ liệu — SPEC-LOG-03."""
    if isinstance(value, str):
        return mask_subscriber(value)
    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(v) for v in value]
    return value


def read_trace(trace_id: str, log_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Đọc lại toàn bộ sự kiện của một mã truy vết.

    Đây là hàm hiện thực đúng tiêu chí nghiệm thu của Session 5. Nếu hàm này
    trả về đủ thông tin để dựng lại một ticket, hệ thống đạt yêu cầu truy vết.
    """
    path = Path(log_path) if log_path else settings.abs_path(settings.log_path)
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("trace_id") == trace_id:
            out.append(row)
    return out
