"""Guardrail đầu ra — SPEC-GUARD-02.

Lớp này chạy trên dự thảo do model sinh, trước khi dự thảo tới màn hình duyệt.
Nó bắt bốn loại lỗi mà model nhỏ mắc thường xuyên nhất trong bài toán này:

* **Cam kết tiền bạc không có căn cứ.** Nghiêm trọng nhất. Một dự thảo hứa
  "hoàn 100% cước tháng này" trở thành nghĩa vụ của doanh nghiệp ngay khi giao
  dịch viên bấm duyệt mà không đọc kỹ.
* **Trích dẫn bịa.** Mã tài liệu trông đúng định dạng nhưng không có trong kho.
* **Rò rỉ thông tin cá nhân** vào nội dung gửi khách hàng.
* **Hứa mốc thời gian** không có trong chính sách.

Guardrail đầu ra không sửa dự thảo. Nó gắn cờ và đẩy sang người duyệt. Việc để
máy tự sửa lỗi của máy sẽ che mất tín hiệu mà Session 6 cần để cải tiến.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

_MONEY_COMMIT = [
    (r"(hoàn|bồi thường|đền|trả lại|miễn)\s+(lại\s+)?(100%|toàn bộ|tất cả)", "cam kết hoàn toàn bộ"),
    (
        r"(hoàn|bồi thường|đền|miễn|giảm)\s+[^.]{0,20}?\d[\d.,]*\s*(đ|vnđ|vnd|đồng|nghìn|triệu)",
        "cam kết số tiền cụ thể",
    ),
    (r"(chắc chắn|cam kết|bảo đảm)\s+[^.]{0,30}(hoàn|bồi thường|đền)", "cam kết chắc chắn về bồi thường"),
]

_TIME_COMMIT = [
    (
        r"(trong|sau)\s+(vòng\s+)?\d+\s*(phút|giờ|ngày|tuần)\s+[^.]{0,25}(sẽ|xong|hoàn tất|khắc phục|xử lý)",
        "hứa mốc thời gian",
    ),
    (r"(ngay lập tức|ngay bây giờ)\s+[^.]{0,20}(khắc phục|xử lý xong|hoàn tất)", "hứa xử lý tức thì"),
]

_PII_LEAK = [
    (re.compile(r"\b\d{12}\b"), "số căn cước"),
    (re.compile(r"\b0\d{9}\b"), "số thuê bao chưa che"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "địa chỉ thư điện tử"),
]

_CITATION = re.compile(r"\[KB-\d{3}\s+v[\d.]+,\s*hiệu lực\s*\d{4}-\d{2}-\d{2}\]")

MIN_WORDS = 40
MAX_WORDS = 260


@dataclass
class OutputCheck:
    """Kết quả kiểm tra một dự thảo phản hồi."""

    passed: bool
    escalate: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Dạng từ điển để ghi nhật ký."""
        return {
            "passed": self.passed,
            "escalate": self.escalate,
            "violations": self.violations,
            "warnings": self.warnings,
        }


def check_output(
    draft_text: str,
    *,
    allowed_doc_ids: set[str] | None = None,
    context_text: str = "",
) -> OutputCheck:
    """Kiểm tra dự thảo trước khi đưa lên màn hình duyệt.

    Args:
        draft_text: Nội dung dự thảo.
        allowed_doc_ids: Các mã tài liệu thực sự đã truy hồi được.
        context_text: Khối ngữ cảnh đã đưa vào prompt, dùng để xác minh con số
            tiền trong dự thảo có nguồn gốc hay không.

    Returns:
        ``OutputCheck``. ``passed=False`` nghĩa là dự thảo không được hiển thị
        như một bản nháp sẵn sàng gửi; ticket chuyển sang luồng người xử lý.
    """
    # TODO(LAB-5): SPEC-GUARD-02 — chặn cam kết tiền vô căn cứ, trích dẫn bịa, rò rỉ PII
    #   Chạy "uv run pytest -m lab5" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-5: SPEC-GUARD-02 — chặn cam kết tiền vô căn cứ, trích dẫn bịa, rò rỉ PII")


def _grounded_in_context(snippet: str, context_text: str) -> bool:
    """Kiểm tra thô xem các con số trong đoạn trích có xuất hiện trong ngữ cảnh không."""
    if not context_text:
        return False
    numbers = re.findall(r"\d[\d.,]*", snippet)
    return bool(numbers) and all(n in context_text for n in numbers)
