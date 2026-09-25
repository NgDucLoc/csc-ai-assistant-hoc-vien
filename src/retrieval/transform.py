"""Query Transformation (slide 39, bước Query Transformation).

Khách hàng viết "tự nhiên mất tiền", tài liệu viết "khấu trừ cước dịch vụ giá trị gia tăng". Viết
lại truy vấn (dùng model) thu hẹp khoảng cách đó, nhưng chưa chắc luôn có lợi: phải đo lại.
"""

from __future__ import annotations

from src.agent.loader import load_prompt
from src.llm.client import LLMClient, get_client


def rewrite_query(ticket_text: str, category: str, *, client: LLMClient | None = None) -> str | None:
    """Viết lại lời phàn nàn thành truy vấn tra cứu chính sách.

    Trả về None khi model không phản hồi được, để bên gọi rơi về truy vấn gốc thay vì dừng cả quy
    trình (suy giảm có kiểm soát, SPEC-ARCH-02 nguyên tắc 3).
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
