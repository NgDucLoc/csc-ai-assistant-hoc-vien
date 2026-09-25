"""Context Assembly — Select, Transform, Assemble (slide 24; slide 25 "more context ≠ better context").

Từ các đoạn tri thức đã truy hồi, chọn những đoạn còn vừa ngân sách, chuyển về dạng có trích dẫn và
ghép thành khối văn bản chèn vào prompt. Ngân sách đo bằng số ký tự (ước lượng khoảng 3.2 ký tự
mỗi token, tổng context tối đa 3.000 token — SPEC-INFRA-04).
"""

from __future__ import annotations

from src.retrieval.models import Hit


def assemble_context(hits: list[Hit], max_chars: int = 2000) -> str:
    """Ghép các đoạn thành khối ngữ cảnh có trích dẫn, trong ngân sách ký tự.

    Mỗi đoạn có dạng ``[KB-001 v1.0, hiệu lực 2026-01-01] Tiêu đề tài liệu — Tiêu đề mục`` xuống dòng
    rồi nội dung. Các đoạn cách nhau một dòng trống, theo đúng thứ tự ``hits``.

    Args:
        hits: Kết quả truy hồi, đã sắp theo điểm.
        max_chars: Ngân sách ký tự. Đoạn đầu tiên không vừa ngân sách thì dừng, không cắt cụt giữa đoạn.

    Returns:
        Khối ngữ cảnh. Chuỗi rỗng nếu không có đoạn nào.
    """
    # TODO(LAB-3): Assemble — ghép đoạn có trích dẫn trong ngân sách ký tự, không cắt cụt giữa đoạn
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Assemble — ghép đoạn có trích dẫn trong ngân sách ký tự, không cắt cụt giữa đoạn")
