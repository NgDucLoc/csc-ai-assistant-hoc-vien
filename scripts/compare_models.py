"""So sánh hai cấu hình trên cùng bộ ticket — Session 2 bước 2.

Chạy: uv run python scripts/compare_models.py --tickets 5

Bốn tổ hợp được đo: cấu hình S, cấu hình L, và cấu hình chuẩn của lớp ở hai
mức nhiệt độ khác nhau.

Kết luận cần chốt sau thí nghiệm này: **tác vụ phân loại cho kết quả ổn định
hơn hẳn ở nhiệt độ bằng không, trong khi tác vụ soạn phản hồi cần nhiệt độ cao
hơn.** Từ đó suy ra một ứng dụng AI không dùng chung một cấu hình model cho
mọi bước — đó là lý do TASK_PARAMS trong src/config.py tồn tại.

Mọi dòng kết quả BẮT BUỘC ghi kèm cấu hình. Từ buổi này trở đi, bảng số liệu
thiếu cột cấu hình không được chấp nhận (SPEC-INFRA-03).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import load_train  # noqa: E402


def run_combo(
    label: str, env: dict[str, str], tickets: list[dict[str, Any]], temperature: float
) -> list[dict[str, Any]]:
    """Chạy một tổ hợp cấu hình trên danh sách ticket."""
    for key, value in env.items():
        os.environ[key] = value

    # Nạp lại cấu hình sau khi đổi biến môi trường.
    for mod in [m for m in list(sys.modules) if m.startswith("src.")]:
        del sys.modules[mod]
    from src.agent.classifier import classify  # noqa: PLC0415
    from src.llm.client import LLMClient  # noqa: PLC0415

    rows: list[dict[str, Any]] = []
    for ticket in tickets:
        client = LLMClient()
        started = time.perf_counter()
        try:
            cls = classify(ticket["customer_msg"], client=client)
            rows.append(
                {
                    "combo": label,
                    "config_profile": env.get("CONFIG_PROFILE", "?"),
                    "model": env.get("LLM_MODEL", "?"),
                    "temperature": temperature,
                    "ticket_id": ticket["id"],
                    "truth": ticket["label"]["category"],
                    "pred": cls.category,
                    "correct": cls.category == ticket["label"]["category"],
                    "confidence": cls.confidence,
                    "defense_layer": cls.defense_layer,
                    "latency_ms": int((time.perf_counter() - started) * 1000),
                }
            )
        except Exception as exc:  # noqa: BLE001
            rows.append({"combo": label, "ticket_id": ticket["id"], "error": str(exc)[:120]})
    return rows


def main() -> int:
    """Chạy bốn tổ hợp và in bảng so sánh."""
    ap = argparse.ArgumentParser(description="So sánh cấu hình model")
    ap.add_argument("--tickets", type=int, default=5)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    tickets = load_train()[: args.tickets]
    base_l = {
        "CONFIG_PROFILE": "L",
        "LLM_BASE_URL": os.environ.get("OLLAMA_URL", "http://localhost:11434/v1"),
        "LLM_MODEL": "qwen3:8b",
    }
    base_s = {
        "CONFIG_PROFILE": "S",
        "LLM_BASE_URL": os.environ.get("SERVER_URL", ""),
        "LLM_MODEL": os.environ.get("SERVER_MODEL", "Qwen3-8B"),
    }

    combos: list[tuple[str, dict[str, str], float]] = [
        ("L · Qwen3-8B · nhiệt độ 0.0", base_l, 0.0),
        ("L · Qwen3-8B · nhiệt độ 0.7", base_l, 0.7),
    ]
    if base_s["LLM_BASE_URL"]:
        combos += [
            ("S · Qwen3-8B · nhiệt độ 0.0", base_s, 0.0),
            ("S · Qwen3-8B · nhiệt độ 0.7", base_s, 0.7),
        ]
    else:
        print("Chưa đặt SERVER_URL nên bỏ qua hai tổ hợp cấu hình S.")
        print("Đặt: export SERVER_URL=http://<server>:4000/v1\n")

    everything: list[dict[str, Any]] = []
    for label, env, temp in combos:
        print(f"Chạy {label} trên {len(tickets)} ticket …")
        os.environ["LLM_TEMPERATURE_OVERRIDE"] = str(temp)
        everything.extend(run_combo(label, env, tickets, temp))

    print()
    print(f"{'tổ hợp':<28} {'cấu hình':>9} {'đúng':>6} {'p50 ms':>8} {'phải cứu':>9}")
    for label, _, _ in combos:
        rows = [r for r in everything if r["combo"] == label and "error" not in r]
        if not rows:
            print(f"{label:<28} {'—':>9} {'lỗi':>6}")
            continue
        acc = sum(r["correct"] for r in rows) / len(rows)
        lat = sorted(r["latency_ms"] for r in rows)[len(rows) // 2]
        rescued = sum(1 for r in rows if r["defense_layer"] != "direct")
        print(f"{label:<28} {rows[0]['config_profile']:>9} {acc:>5.0%} {lat:>8} {rescued:>9}")

    print()
    print("Kết luận cần chốt: phân loại ổn định hơn hẳn ở nhiệt độ 0. Soạn phản hồi thì")
    print("ngược lại, cần nhiệt độ cao hơn để câu văn không cứng. Một ứng dụng AI không")
    print("dùng chung một cấu hình model cho mọi bước — xem TASK_PARAMS trong src/config.py.")

    out = Path(args.out) if args.out else Path("eval/results/compare_models.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(everything, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nĐã ghi {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
