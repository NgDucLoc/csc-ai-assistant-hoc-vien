"""Knowledge Embedding — Embed (slide 39 Chunk → Embed → Index).

Embedding biến một đoạn chữ thành một dãy số (vector) sao cho các đoạn có nghĩa gần nhau nằm gần
nhau (slide 40, semantic search). Việc gọi model embedding đi qua ``LLMClient.embed`` — không
được gọi model ở nơi khác (SPEC-ARCH-02 nguyên tắc 2). Model embedding phải giống nhau ở cả hai
cấu hình S và L (SPEC-INFRA-01), nếu không chỉ mục dựng ở cấu hình này không đọc được ở cấu hình kia.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.knowledge.preparation import Chunk


def embed_chunks(
    chunks: list[Chunk],
    client: Any,
    *,
    batch_size: int = 16,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[list[float]]:
    """Tạo vector nhúng cho danh sách đoạn, gọi model theo lô.

    Args:
        chunks: Danh sách đoạn cần nhúng.
        client: Đối tượng có phương thức ``embed(texts) -> list[list[float]]`` (thường là ``LLMClient``).
        batch_size: Số đoạn gửi trong một lời gọi.
        on_progress: Hàm gọi sau mỗi lô với (số đoạn đã nhúng, tổng số đoạn). Có thể bỏ trống.

    Returns:
        Danh sách vector, cùng thứ tự với ``chunks``.

    Raises:
        ValueError: ``batch_size`` nhỏ hơn 1, hoặc model trả về số vector khác số đoạn đã gửi.
    """
    # TODO(LAB-3): Embed — gọi model embedding theo lô, giữ nguyên thứ tự đoạn
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Embed — gọi model embedding theo lô, giữ nguyên thứ tự đoạn")
