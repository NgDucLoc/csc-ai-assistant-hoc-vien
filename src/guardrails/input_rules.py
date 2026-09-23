"""Guardrail đầu vào — SPEC-GUARD-01.

Ba việc lớp này làm, theo thứ tự:

1. **Phát hiện chèn lệnh.** Ticket là dữ liệu do người ngoài viết. Câu
   "bỏ qua hướng dẫn phía trên" nằm trong ticket phải bị coi là nội dung cần
   phân loại, không phải chỉ thị. Việc phân tách bằng thẻ ``<ticket>`` trong
   prompt là lớp phòng vệ thứ nhất; lớp này là thứ hai.
2. **Che thông tin cá nhân.** Dữ liệu có 3 ticket cố ý chứa thông tin nhạy cảm
   (SPEC-DATA-05). Số căn cước, số tài khoản ngân hàng và địa chỉ nhà bị che
   trước khi bất kỳ thứ gì được gửi lên model hoặc ghi vào nhật ký.
3. **Chặn ticket rác.** Nội dung vô nghĩa được chuyển người ngay, không tiêu
   tốn lời gọi model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Các mẫu chèn lệnh thường gặp. Danh sách này cố ý ngắn và dễ đọc: mục tiêu là
# dạy nguyên lý, không phải xây một bộ lọc hoàn hảo. Phần mở rộng ở CHALLENGE.md.
_INJECTION_PATTERNS = [
    (r"bỏ qua (mọi |các |toàn bộ )?(hướng dẫn|chỉ dẫn|quy tắc|lệnh)", "yêu cầu bỏ qua hướng dẫn"),
    (
        r"(ignore|disregard|forget)\s+(all\s+|the\s+|previous\s+)*(instruction|prompt|rule)",
        "injection tiếng Anh",
    ),
    (r"(bạn|mày) (giờ|bây giờ) là", "yêu cầu đổi vai trò"),
    (r"(you are|act as|pretend to be)\s+(now\s+)?a", "yêu cầu đổi vai trò tiếng Anh"),
    (
        r"(in ra|cho (tôi|xem)|tiết lộ|hiển thị)\s+(prompt|câu lệnh hệ thống|system prompt)",
        "dò hỏi prompt hệ thống",
    ),
    (r"(system prompt|reveal your instruction)", "dò hỏi prompt hệ thống tiếng Anh"),
    (r"(thông tin|dữ liệu|cước|số dư) (của )?(thuê bao|số) (khác|người khác|0\d{9})", "dò hỏi thuê bao khác"),
]

# Thông tin cá nhân cần che trước khi rời khỏi biên hệ thống.
_PII_PATTERNS = [
    (re.compile(r"\b\d{12}\b"), "CCCD", lambda m: m.group(0)[:3] + "*" * 9),
    (re.compile(r"\b\d{9}\b(?!\d)"), "CMND", lambda m: m.group(0)[:3] + "*" * 6),
    (re.compile(r"\b\d{10,16}\b"), "STK", lambda m: m.group(0)[:4] + "*" * (len(m.group(0)) - 4)),
    (
        re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
        "email",
        lambda m: m.group(0).split("@")[0][:2] + "***@" + m.group(0).split("@")[1],
    ),
]

_SUBSCRIBER = re.compile(r"\b(0\d{2})(\d{7})\b")

MIN_MEANINGFUL_CHARS = 15


@dataclass
class InputCheck:
    """Kết quả kiểm tra đầu vào."""

    text: str  # nội dung đã che thông tin cá nhân
    blocked: bool
    escalate: bool
    findings: list[str] = field(default_factory=list)
    pii_types: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Dạng từ điển để ghi nhật ký."""
        return {
            "blocked": self.blocked,
            "escalate": self.escalate,
            "findings": self.findings,
            "pii_types": self.pii_types,
        }


def mask_subscriber(text: str) -> str:
    """Che một phần số thuê bao — SPEC-DATA-01.

    Số thuê bao phải được che trong MỌI hiển thị, kể cả nhật ký và ảnh chụp màn
    hình dùng để nộp bài.
    """
    return _SUBSCRIBER.sub(lambda m: f"{m.group(1)}xxxxxxx", text)


def mask_pii(text: str) -> tuple[str, list[str]]:
    """Che thông tin cá nhân nhạy cảm.

    Returns:
        Cặp (văn bản đã che, danh sách loại thông tin đã phát hiện).
    """
    found: list[str] = []
    out = text
    for pattern, label, replace in _PII_PATTERNS:
        if pattern.search(out):
            found.append(label)
            out = pattern.sub(replace, out)
    return mask_subscriber(out), sorted(set(found))


def detect_injection(text: str) -> list[str]:
    """Tìm dấu hiệu chèn lệnh trong nội dung ticket."""
    low = text.lower()
    return [label for pattern, label in _INJECTION_PATTERNS if re.search(pattern, low)]


def is_junk(text: str) -> bool:
    """Nhận diện ticket rác: quá ngắn, hoặc gần như không có chữ cái."""
    stripped = text.strip()
    if len(stripped) < MIN_MEANINGFUL_CHARS:
        return True
    letters = sum(1 for ch in stripped if ch.isalpha())
    return letters / len(stripped) < 0.4


def check_input(text: str) -> InputCheck:
    """Chạy đủ ba kiểm tra đầu vào trên một ticket.

    Lưu ý thiết kế: phát hiện chèn lệnh **không chặn** ticket. Ticket vẫn được
    xử lý, nhưng bị đánh dấu chuyển người. Chặn thẳng sẽ khiến một khách hàng
    viết vô tình đúng mẫu bị mất luôn yêu cầu chính đáng của mình.
    """
    # TODO(LAB-4): Ba kiểm tra đầu vào: chèn lệnh, thông tin cá nhân, ticket rác
    #   Chạy "uv run pytest -m lab4" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-4: Ba kiểm tra đầu vào: chèn lệnh, thông tin cá nhân, ticket rác")
