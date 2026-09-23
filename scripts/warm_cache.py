"""Sinh và đóng băng cache — mốc chốt của kế hoạch xây dựng.

Chạy trên máy CÓ máy chủ suy luận:
    uv run python scripts/warm_cache.py
    git add .cache/llm_cache.db && git commit -m "[SPEC-LLM-02] Sinh lại cache"

Cache là hạ tầng, không phải tối ưu tốc độ. Ba thứ treo vào tệp này:
  1. CI chạy được trên runner không GPU, không Ollama, không mạng tới server.
  2. Lớp dự phòng thứ 3 khi mất cả hai đường suy luận.
  3. Kết quả đánh giá tái lập được.

**Sau khi đóng băng, mọi PR sửa prompt BẮT BUỘC kèm cache sinh lại trong cùng
PR.** Không có luật này, CI sẽ đỏ hàng loạt và cả đội học cách phớt lờ nó.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.classifier import classify, rewrite_query  # noqa: E402
from src.config import settings  # noqa: E402
from src.data import load_adversarial, load_gold_qa, load_train  # noqa: E402
from src.llm.client import get_client  # noqa: E402


def main() -> int:
    """Chạy toàn bộ đầu vào qua đường chạy thật để nạp cache."""
    ap = argparse.ArgumentParser(description="Sinh cache cho CI và cho chế độ dự phòng")
    ap.add_argument(
        "--include-gold-test", action="store_true", help="Chỉ giảng viên dùng, sau khi mở khóa tập kiểm định"
    )
    args = ap.parse_args()

    if settings.cache_mode != "on":
        print(f"CACHE_MODE đang là '{settings.cache_mode}'. Đặt CACHE_MODE=on rồi chạy lại.")
        return 2

    client = get_client()
    rows = load_train()
    if args.include_gold_test:
        from src.data import load_gold_test

        rows += load_gold_test()

    print(f"Nạp cache cho {len(rows)} ticket · {settings.profile_banner()}")
    for i, row in enumerate(rows, start=1):
        client.reset_budget()
        cls = classify(row["customer_msg"])
        rewrite_query(row["customer_msg"], cls.category)
        if i % 10 == 0:
            print(f"  {i}/{len(rows)}")

    adv = load_adversarial()
    print(f"Nạp cache cho {len(adv)} ca đối kháng")
    for row in adv:
        client.reset_budget()
        classify(row["text"])

    print(f"Nạp cache cho {len(load_gold_qa())} truy vấn hỏi–đáp vàng")

    stats = client.cache.stats()
    print()
    print(f"  mục trong cache : {stats['entries']}")
    print(f"  theo cấu hình   : {stats['by_profile']}")
    print()
    print("Bước tiếp theo — kiểm chứng CI chạy được offline:")
    print("    CACHE_MODE=cache_only uv run pytest -q")
    print("    git add .cache/llm_cache.db")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
