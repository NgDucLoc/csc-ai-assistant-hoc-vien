"""Thí nghiệm nhiệt độ — Session 2 bước 3.

Chạy: uv run python scripts/temperature_demo.py

Hỏi model CÙNG MỘT câu nhiều lần ở hai mức nhiệt độ, rồi đếm xem model đưa ra
bao nhiêu câu trả lời KHÁC NHAU. Hai tác vụ được thử trên cùng một ticket:

1. Chọn nhóm cho ticket — cần một đáp án đúng, lặp lại được.
2. Soạn phản hồi cho khách — cần câu chữ tự nhiên, không lặp lại máy móc.

Kết luận cần tự rút ra từ số đo: một ứng dụng AI không dùng chung một cấu hình
model cho mọi bước — đó là lý do ``TASK_PARAMS`` trong ``src/config.py`` tồn tại.

Script chỉ dùng ``LLMClient`` và dữ liệu có sẵn, không cần phần mã của Lab 3–4.
Cache bị tắt có chủ ý: bật cache thì cùng một câu hỏi luôn trả về cùng một câu
trả lời đã lưu, và thí nghiệm này mất hết ý nghĩa.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

os.environ["CACHE_MODE"] = "off"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings  # noqa: E402
from src.data import load_train  # noqa: E402
from src.llm.client import LLMClient  # noqa: E402

CATEGORIES = (
    "cuoc_thanh_toan",
    "chat_luong_ket_noi",
    "goi_cuoc_khuyen_mai",
    "thiet_bi_sim",
    "thong_tin_thue_bao",
    "khac",
)
TEMPERATURES = (0.0, 0.7)
MAX_TOKENS = 800

SYSTEM_CLASSIFY = (
    "Bạn là bộ phân loại ticket chăm sóc khách hàng viễn thông. "
    "Chỉ trả lời bằng đúng MỘT mã nhóm trong danh sách, không giải thích."
)
SYSTEM_REPLY = (
    "Bạn là giao dịch viên chăm sóc khách hàng viễn thông. "
    "Viết đúng hai câu phản hồi lịch sự bằng tiếng Việt. Không hứa hẹn bồi thường."
)


def pick_category(answer: str) -> str:
    """Tìm mã nhóm xuất hiện sớm nhất trong câu trả lời của model."""
    low = answer.lower()
    found = [(low.find(c), c) for c in CATEGORIES if c in low]
    return min(found)[1] if found else "(không nhận ra)"


def normalize(text: str) -> str:
    """Chuẩn hóa để hai câu chỉ khác dấu cách hay chữ hoa vẫn tính là một."""
    return re.sub(r"\s+", " ", text).strip().lower()


def ask(client: LLMClient, *, task: str, system: str, user: str, temperature: float) -> tuple[str, int]:
    """Hỏi model một lần, trả về (câu trả lời, độ trễ mili giây)."""
    started = time.perf_counter()
    resp = client.complete(
        task=task,
        system=system,
        user=user,
        params={"temperature": temperature, "max_tokens": MAX_TOKENS},
    )
    return resp.text.strip(), int((time.perf_counter() - started) * 1000)


def main() -> int:
    """Chạy thí nghiệm và in bảng kết quả."""
    ap = argparse.ArgumentParser(description="Thí nghiệm nhiệt độ")
    ap.add_argument("--tickets", type=int, default=2, help="Số ticket mơ hồ dùng để thử")
    ap.add_argument("--repeats", type=int, default=4, help="Số lần hỏi lại mỗi câu")
    args = ap.parse_args()

    tickets = [t for t in load_train() if t["meta"].get("is_ambiguous")][: args.tickets]
    client = LLMClient(budget=10_000)
    print(f"Cấu hình đang chạy: {settings.profile_banner()}")
    print(f"{len(tickets)} ticket mơ hồ × {args.repeats} lần hỏi × {len(TEMPERATURES)} nhiệt độ × 2 tác vụ")
    print("Mỗi lần hỏi mất vài giây; cả thí nghiệm mất vài phút. Đừng tắt giữa chừng.\n")

    rows: list[tuple[str, float, str, int, int, list[str]]] = []
    for ticket in tickets:
        text = ticket["customer_msg"]
        print(f"--- {ticket['id']}: {text[:90]}{'…' if len(text) > 90 else ''}")
        for temp in TEMPERATURES:
            labels: list[str] = []
            replies: list[str] = []
            latencies: list[int] = []
            for _ in range(args.repeats):
                answer, ms = ask(
                    client,
                    task="classify",
                    system=SYSTEM_CLASSIFY,
                    user=f"Danh sách nhóm: {', '.join(CATEGORIES)}\n\nTicket:\n{text}\n\nNhóm:",
                    temperature=temp,
                )
                labels.append(pick_category(answer))
                latencies.append(ms)
                answer, ms = ask(
                    client, task="generate", system=SYSTEM_REPLY, user=f"Ticket:\n{text}", temperature=temp
                )
                replies.append(answer)
                latencies.append(ms)
            latencies.sort()
            p50 = latencies[len(latencies) // 2]
            rows.append((ticket["id"], temp, "chọn nhóm", len({*labels}), args.repeats, labels))
            distinct_replies = len({normalize(r) for r in replies})
            rows.append((ticket["id"], temp, "soạn phản hồi", distinct_replies, args.repeats, replies))
            print(f"    nhiệt độ {temp}: xong ({p50} ms/lần, giữa)")

    print("\nKẾT QUẢ — số câu trả lời KHÁC NHAU trên số lần hỏi")
    print(f"{'ticket':<10} {'nhiệt độ':>9}  {'tác vụ':<14} {'khác nhau':>10}")
    for ticket_id, temp, task, distinct, total, _ in rows:
        print(f"{ticket_id:<10} {temp:>9}  {task:<14} {distinct:>4} / {total}")

    print("\nCHI TIẾT — đọc kỹ phần này, số liệu chưa đủ để kết luận")
    for ticket_id, temp, task, _, _, answers in rows:
        print(f"\n[{ticket_id} · nhiệt độ {temp} · {task}]")
        for i, a in enumerate(answers, 1):
            print(f"  {i}. {a[:200]}{'…' if len(a) > 200 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
