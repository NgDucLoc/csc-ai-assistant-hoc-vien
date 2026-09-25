"""Filter — lọc siêu dữ liệu và quyết định có đủ căn cứ hay không (slide 39, slide 44).

Hai việc khác nhau:

* ``filter_hits`` loại kết quả theo siêu dữ liệu (nhóm, ngày hiệu lực) — chống Stale Retrieval.
* ``judge_evidence`` quyết định kết quả còn lại có đủ căn cứ để trả lời không (SPEC-RAG-03).
"""

from __future__ import annotations

from src.retrieval.models import Hit


def filter_hits(
    hits: list[Hit], *, categories: set[str] | None = None, as_of: str | None = None
) -> list[Hit]:
    """Lọc kết quả theo siêu dữ liệu.

    Args:
        hits: Kết quả đã sắp theo điểm.
        categories: Chỉ giữ các đoạn thuộc những nhóm này. Bỏ trống thì không lọc.
        as_of: Ngày (``YYYY-MM-DD``). Chỉ giữ các đoạn có ``effective_date`` không muộn hơn ngày này.

    Returns:
        Danh sách còn lại, giữ nguyên thứ tự.
    """
    out = hits
    if categories:
        out = [h for h in out if h.category in categories]
    if as_of:
        out = [h for h in out if h.effective_date <= as_of]
    return out


def judge_evidence(hits: list[Hit], min_score: float) -> tuple[bool, str]:
    """Quyết định có đủ căn cứ để trả lời không — SPEC-RAG-03.

    Đây là ranh giới an toàn quan trọng nhất của toàn hệ thống: một trợ lý bịa ra chính sách gây rủi
    ro nghiệp vụ nghiêm trọng hơn nhiều so với một trợ lý im lặng và chuyển người (ADR-0005). Ranh
    giới nằm ở đúng ba nhánh so sánh dưới đây.

    Args:
        hits: Kết quả đã sắp giảm dần theo điểm.
        min_score: Ngưỡng điểm tối thiểu của kết quả đứng đầu.

    Returns:
        Cặp (đủ căn cứ, lý do). Lý do không đủ căn cứ chứa cụm "Không đủ căn cứ" hoặc
        "Kho tri thức không trả về kết quả nào".
    """
    # TODO(LAB-3): Filter — điểm cao nhất dưới ngưỡng thì KHÔNG đủ căn cứ, chuyển người
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Filter — điểm cao nhất dưới ngưỡng thì KHÔNG đủ căn cứ, chuyển người")
