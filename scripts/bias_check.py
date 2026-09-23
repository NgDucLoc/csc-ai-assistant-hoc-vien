"""Kiểm tra thiên lệch của hệ thống — SPEC-RESP-01, Session 6.

Chạy: uv run python scripts/bias_check.py

Câu hỏi cần trả lời: **hệ thống có xử lý khác nhau giữa các nhóm khách hàng
không?** Với bài toán phân loại ticket, "nhóm khách hàng" được xấp xỉ bằng ba
chiều đo được ngay trên bộ dữ liệu kiểm định:

  1. **Văn phong** — ticket dài, đầy đủ so với ticket ngắn, viết tắt.
  2. **Sắc thái** — khách hàng điềm đạm so với khách hàng gay gắt.
  3. **Kênh tiếp nhận** — app, tổng đài, thư điện tử.

Nếu độ chính xác chênh lệch đáng kể giữa các nhóm, hệ thống đang phục vụ tốt
một kiểu khách hàng và kém với kiểu khác. Đó là một giới hạn phải ghi vào
Model Card, không phải một con số để giấu đi.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.workflow import process_ticket  # noqa: E402
from src.config import ROOT, settings  # noqa: E402
from src.data import load_gold_test  # noqa: E402

SHORT_THRESHOLD = 20  # số từ


def group_by_style(row: dict[str, Any]) -> str:
    """Nhóm theo độ dài và mức trau chuốt của văn phong."""
    words = len(row["customer_msg"].split())
    return "ngắn gọn" if words < SHORT_THRESHOLD else "đầy đủ"


def group_by_sentiment(row: dict[str, Any]) -> str:
    """Nhóm theo sắc thái khách hàng."""
    return row["label"]["sentiment"]


def group_by_channel(row: dict[str, Any]) -> str:
    """Nhóm theo kênh tiếp nhận."""
    return row["channel"]


DIMENSIONS: dict[str, Callable[[dict[str, Any]], str]] = {
    "văn phong": group_by_style,
    "sắc thái": group_by_sentiment,
    "kênh": group_by_channel,
}

GAP_WARNING = 0.15  # chênh lệch trên 15 điểm phần trăm là đáng ghi vào Model Card


def main() -> int:
    """Chạy kiểm tra thiên lệch trên tập kiểm định."""
    ap = argparse.ArgumentParser(description="Kiểm tra thiên lệch")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = load_gold_test()
    if args.limit:
        rows = rows[: args.limit]

    print(f"KIỂM TRA THIÊN LỆCH · {len(rows)} ticket · {settings.profile_banner()}\n")

    outcomes: list[dict[str, Any]] = []
    for i, row in enumerate(rows, start=1):
        result = process_ticket(row["id"], row["customer_msg"])
        outcomes.append(
            {
                "row": row,
                "correct": (result.classification or {}).get("category") == row["label"]["category"],
                "escalated": result.status.value == "escalated",
                "latency_ms": result.total_ms,
            }
        )
        if i % 10 == 0:
            print(f"  {i}/{len(rows)}")

    report: dict[str, Any] = {
        "config_profile": settings.config_profile,
        "dataset_size": len(rows),
        "dimensions": {},
    }

    for dim_name, fn in DIMENSIONS.items():
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for out in outcomes:
            buckets[fn(out["row"])].append(out)

        stats: dict[str, Any] = {}
        for group, items in sorted(buckets.items()):
            if not items:
                continue
            stats[group] = {
                "count": len(items),
                "accuracy": round(sum(i["correct"] for i in items) / len(items), 4),
                "escalation_rate": round(sum(i["escalated"] for i in items) / len(items), 4),
                "mean_latency_ms": int(sum(i["latency_ms"] for i in items) / len(items)),
            }

        usable = {g: s for g, s in stats.items() if s["count"] >= 3}
        if len(usable) > 1:
            accs = [s["accuracy"] for s in usable.values()]
            gap = max(accs) - min(accs)
        else:
            gap = 0.0
        report["dimensions"][dim_name] = {
            "groups": stats,
            "accuracy_gap": round(gap, 4),
            "flagged": gap > GAP_WARNING,
        }

        print(f"\n── theo {dim_name} " + "─" * (44 - len(dim_name)))
        print(f"{'nhóm':<16} {'số ca':>6} {'chính xác':>12} {'chuyển người':>13}")
        for group, s in stats.items():
            note = "" if s["count"] >= 3 else "  (quá ít ca)"
            print(
                f"{group:<16} {s['count']:>6} {s['accuracy']:>11.0%} " f"{s['escalation_rate']:>12.0%}{note}"
            )
        if gap > GAP_WARNING:
            print(
                f"  ⚠ Chênh lệch {gap:.0%} giữa nhóm cao nhất và thấp nhất — "
                f"vượt ngưỡng {GAP_WARNING:.0%}."
            )
            print("     Đây là một giới hạn phải ghi vào Model Card, không phải con số để giấu.")
        else:
            print(f"  Chênh lệch {gap:.0%}, trong ngưỡng chấp nhận.")

    out = Path(args.out) if args.out else ROOT / "eval" / "results" / "bias_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nĐã ghi {out.relative_to(ROOT)}")
    print("\nLƯU Ý: tập kiểm định 40 ticket là nhỏ. Chênh lệch trên một nhóm dưới 5 ca")
    print("chưa đủ căn cứ kết luận. Nêu rõ giới hạn này trong Model Card.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
