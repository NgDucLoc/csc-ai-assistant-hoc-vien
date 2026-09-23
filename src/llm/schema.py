"""Bốn lớp phòng vệ cho đầu ra có cấu trúc — SPEC-LLM-04.

Model 3 tỉ tham số chắc chắn sẽ trả về sai định dạng ở một số trường hợp. Đó
không phải sự cố mà là tiền đề thiết kế của module này. Bài học cần chốt lại
với học viên ở Session 3 bước 2: **một ứng dụng AI đáng tin không phải nhờ
model giỏi, mà nhờ tầng xử lý bao quanh model.**

Bốn lớp, theo thứ tự áp dụng:

1. Khai báo lược đồ — nói rõ định dạng mong muốn ngay trong prompt.
2. Bóc tách — gỡ lời dẫn, khối mã, văn bản thừa quanh JSON.
3. Thử lại có phản hồi lỗi — tối đa 2 lần, đưa chính thông báo lỗi vào prompt.
4. Dự phòng — trả về bản ghi đánh dấu ``needs_human`` thay vì ném lỗi.

Lớp 4 là lý do hệ thống không bao giờ dừng đột ngột: đầu ra hỏng trở thành
một ca chuyển người, đúng tinh thần suy giảm có kiểm soát của SPEC-ARCH-02.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
_FIRST_OBJ = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class ParseOutcome:
    """Kết quả của một lần phân tích đầu ra có cấu trúc."""

    data: dict[str, Any]
    ok: bool
    attempts: int
    layer: str
    errors: list[str] = field(default_factory=list)


# --- Lớp 2: bóc tách -------------------------------------------------------
def extract_json(raw: str) -> dict[str, Any] | None:
    """Bóc đối tượng JSON đầu tiên ra khỏi văn bản model trả về.

    Xử lý ba dạng hỏng thường gặp nhất của model nhỏ: bọc trong khối mã, thêm
    lời dẫn kiểu "Đây là kết quả:", và dùng dấu nháy đơn thay vì nháy kép.

    Args:
        raw: Văn bản thô model trả về.

    Returns:
        Từ điển đã phân tích, hoặc None nếu không cứu được.
    """
    # TODO(LAB-3): Lớp 2 — bóc JSON khỏi văn bản thừa: khối mã, lời dẫn, nháy đơn
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Lớp 2 — bóc JSON khỏi văn bản thừa: khối mã, lời dẫn, nháy đơn")


# --- Lớp 1: khai báo lược đồ ----------------------------------------------
def schema_hint(schema: dict[str, Any]) -> str:
    """Sinh đoạn mô tả lược đồ để chèn vào phần ĐỊNH DẠNG ĐẦU RA của prompt."""
    lines = ["Trả về DUY NHẤT một đối tượng JSON, không kèm lời dẫn, không kèm khối mã."]
    lines.append("Các trường bắt buộc:")
    for name, spec in schema.items():
        allowed = spec.get("enum")
        desc = spec.get("desc", "")
        if allowed:
            lines.append(f'  "{name}": một trong {allowed} — {desc}')
        else:
            lines.append(f'  "{name}": {spec.get("type", "string")} — {desc}')
    return "\n".join(lines)


def validate(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Kiểm tra một từ điển theo lược đồ rút gọn.

    Args:
        data: Dữ liệu đã bóc tách.
        schema: Lược đồ dạng ``{ten_truong: {"type": ..., "enum": [...]}}``.

    Returns:
        Danh sách lỗi. Rỗng nghĩa là hợp lệ.
    """
    # TODO(LAB-3): Lớp 1 — kiểm tra theo lược đồ: kiểu dữ liệu, enum, khoảng giá trị
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Lớp 1 — kiểm tra theo lược đồ: kiểu dữ liệu, enum, khoảng giá trị")


# --- Lớp 3 + 4: thử lại và dự phòng ---------------------------------------
def parse_with_retry(
    call: Callable[[str | None], str],
    schema: dict[str, Any],
    fallback: dict[str, Any],
    *,
    max_retries: int = 2,
) -> ParseOutcome:
    """Chạy đủ bốn lớp phòng vệ cho một lời gọi sinh dữ liệu có cấu trúc.

    Args:
        call: Hàm nhận thông báo lỗi của lần trước (None ở lần đầu) và trả về
            văn bản thô của model. Việc đưa lỗi ngược vào prompt là điểm mấu
            chốt của lớp 3 — bảo model "sai định dạng, làm lại" hiệu quả hơn
            nhiều so với gọi lại y hệt.
        schema: Lược đồ để kiểm tra.
        fallback: Bản ghi trả về khi mọi lần thử đều hỏng. BẮT BUỘC đánh dấu
            cần người xem.
        max_retries: Số lần thử lại tối đa, mặc định 2 theo SPEC-LLM-04.

    Returns:
        ``ParseOutcome`` ghi rõ lớp nào đã cứu được kết quả — số liệu này chính
        là bảng "trước và sau" mà Session 3 bước 2 yêu cầu học viên nộp.
    """
    # TODO(LAB-3): Lớp 3 và 4 — thử lại có đưa lỗi vào prompt, rồi dự phòng needs_human
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Lớp 3 và 4 — thử lại có đưa lỗi vào prompt, rồi dự phòng needs_human")


# --- Lược đồ dùng chung ----------------------------------------------------
CLASSIFICATION_SCHEMA: dict[str, Any] = {
    "category": {
        "type": "string",
        "enum": [
            "cuoc_thanh_toan",
            "chat_luong_ket_noi",
            "goi_cuoc_khuyen_mai",
            "thiet_bi_sim",
            "thong_tin_thue_bao",
            "khac",
        ],
        "desc": "nhóm vấn đề theo SPEC-DATA-03",
    },
    "priority": {"type": "string", "enum": ["P1", "P2", "P3"], "desc": "mức ưu tiên"},
    "sentiment": {
        "type": "string",
        "enum": ["trung_tinh", "buc_boi", "gay_gat"],
        "desc": "sắc thái của khách hàng",
    },
    "confidence": {"type": "number", "min": 0, "max": 1, "desc": "độ tin cậy của chính bạn"},
    "entities": {"type": "object", "desc": "thực thể trích xuất được", "required": False},
    "reason": {"type": "string", "desc": "một câu lý do", "required": False},
}

CLASSIFICATION_FALLBACK: dict[str, Any] = {
    "category": "khac",
    "priority": "P2",
    "sentiment": "trung_tinh",
    "confidence": 0.0,
    "entities": {},
    "reason": "Không phân tích được đầu ra của model.",
}
