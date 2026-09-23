"""Đo năng lực phục vụ của máy chủ suy luận — SPEC-INFRA-02, SPEC-INFRA-05.

Hai công dụng, ở hai thời điểm khác nhau:

**Trước khóa 1 tuần** — đơn vị tổ chức chạy để **chọn cấu hình tham chiếu**.
Cấu hình chuẩn của lớp không được quyết bằng phỏng đoán về năng lực phần cứng
mà bằng phép đo này, đối chiếu bảng quyết định ở SPEC-INFRA-02.

**Session 5 bước 5** — mỗi nhóm đo năng lực phục vụ của hệ thống mình, rồi đối
chiếu với giả định khối lượng ticket đã ghi trong Canvas ở Session 1. Đây là
lúc con số kinh doanh viết ở buổi đầu gặp con số kỹ thuật đo được ở buổi cuối.

**Về khung giờ đo trên cấu hình S:** sáu nhóm cùng đo trên một server sẽ làm
số liệu của nhau nhiễu tới mức không dùng được. Tham số ``--slot`` bắt buộc
đúng khung giờ được phân; script tự từ chối chạy sai khe thay vì trông vào
việc học viên nhớ lịch.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import ROOT, settings  # noqa: E402

PROMPT = (
    "Phân loại ticket sau vào một trong sáu nhóm và trả về JSON: "
    "cuoc_thanh_toan, chat_luong_ket_noi, goi_cuoc_khuyen_mai, thiet_bi_sim, "
    "thong_tin_thue_bao, khac.\n\n<ticket>\nTháng này tôi bị trừ 320 nghìn "
    "trong khi mọi tháng chỉ 149 nghìn, đề nghị kiểm tra lại.\n</ticket>"
)

# Mức đồng thời khác nhau theo cấu hình: cấu hình L chạy trên laptop nên đo
# tới 10 là đủ để thấy quy luật suy giảm. Đo cao hơn chỉ làm treo máy học viên.
CONCURRENCY = {"S": [1, 5, 10, 20], "L": [1, 3, 5, 10]}


def _one_request() -> tuple[bool, float]:
    """Gửi một yêu cầu, trả về (thành công, độ trễ giây)."""
    from src.llm.client import LLMClient

    client = LLMClient(budget=999)
    started = time.perf_counter()
    try:
        client.complete(task="classify", system="Bạn trả về JSON.", user=PROMPT)
        return True, time.perf_counter() - started
    except Exception:  # noqa: BLE001 — thất bại là dữ liệu, không phải sự cố
        return False, time.perf_counter() - started


def measure(concurrency: int, requests: int) -> dict[str, Any]:
    """Đo độ trễ và thông lượng ở một mức đồng thời."""
    latencies: list[float] = []
    failures = 0
    lock = threading.Lock()

    def worker() -> None:
        nonlocal failures
        ok, elapsed = _one_request()
        with lock:
            if ok:
                latencies.append(elapsed)
            else:
                failures += 1

    started = time.perf_counter()
    pending = requests
    while pending > 0:
        batch = min(concurrency, pending)
        threads = [threading.Thread(target=worker) for _ in range(batch)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        pending -= batch
    wall = time.perf_counter() - started

    if not latencies:
        return {
            "concurrency": concurrency,
            "requests": requests,
            "failures": failures,
            "error": "không yêu cầu nào thành công",
        }

    ordered = sorted(latencies)
    p95 = ordered[min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))]
    return {
        "concurrency": concurrency,
        "requests": requests,
        "failures": failures,
        "mean_s": round(statistics.mean(latencies), 2),
        "p50_s": round(statistics.median(latencies), 2),
        "p95_s": round(p95, 2),
        "throughput_rps": round(len(latencies) / wall, 3),
        "tickets_per_hour": int(3600 * len(latencies) / wall),
    }


def decide_reference_profile(rows: list[dict[str, Any]], vram_gb: float | None) -> str:
    """Đối chiếu bảng quyết định của SPEC-INFRA-02.

    Nguyên tắc khi phân vân: chọn cấu hình L. Phải hạ chuẩn giữa khóa vì server
    không tải nổi gây thiệt hại lớn hơn nhiều so với chấp nhận chất lượng đầu
    ra thấp hơn một chút ngay từ đầu.
    """
    at10 = next((r for r in rows if r["concurrency"] == 10 and "p95_s" in r), None)
    if at10 is None:
        return "L — không đo được ở mức đồng thời 10, chọn L cho an toàn"

    p95 = at10["p95_s"]
    if vram_gb is None:
        return f"L — không xác định được VRAM (p95 ở mức 10 là {p95}s). An toàn hơn là hạ chuẩn giữa chừng"
    if p95 > 25:
        return f"L — p95 {p95}s vượt 25s. Cấu hình S chỉ dùng cho phần trình diễn cuối khóa"
    if vram_gb >= 24 and p95 <= 15:
        return f"S — VRAM {vram_gb}GB, p95 {p95}s. Dùng Qwen3-8B bf16 (đủ chỗ dư cho 14B nếu muốn thử)"
    if 16 <= vram_gb < 24 and p95 <= 20:
        return f"S — VRAM {vram_gb}GB, p95 {p95}s. Qwen3-8B lượng tử hóa 4-bit (AWQ)"
    if 8 <= vram_gb < 16 and p95 <= 25:
        return f"S — VRAM {vram_gb}GB, p95 {p95}s. Qwen3-8B 4-bit (AWQ), giảm đồng thời tối đa xuống 15"
    return f"L — VRAM {vram_gb}GB với p95 {p95}s không thỏa bảng quyết định"


def main() -> int:
    """Chạy phép đo và in bảng kết quả."""
    ap = argparse.ArgumentParser(description="Đo năng lực máy chủ suy luận")
    ap.add_argument("--requests", type=int, default=20, help="Số yêu cầu mỗi mức đồng thời")
    ap.add_argument(
        "--vram", type=float, default=None, help="VRAM khả dụng (GB), để đối chiếu bảng quyết định"
    )
    ap.add_argument("--slot", default=None, help="Khung giờ được phân, HH:MM-HH:MM (bắt buộc với cấu hình S)")
    ap.add_argument("--team", default="")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    profile = settings.config_profile

    # --- kiểm tra khung giờ, giải xung đột lịch của Session 5 bước 5 ------
    if profile == "S":
        if not args.slot:
            print("Cấu hình S bắt buộc có --slot. Sáu nhóm cùng đo trên một")
            print("server sẽ làm số liệu của nhau nhiễu tới mức không dùng được.")
            print("Xem bảng phân khe giờ giảng viên phát và chạy lại:")
            print("    uv run python scripts/bench_server.py --slot 09:20-09:25 --team nhom-a")
            return 2
        start_s, _, end_s = args.slot.partition("-")
        now = datetime.now().time()
        start = datetime.strptime(start_s.strip(), "%H:%M").time()
        end = datetime.strptime(end_s.strip(), "%H:%M").time()
        if not (start <= now <= end):
            print(f"Ngoài khung giờ được phân ({args.slot}). Bây giờ là {now.strftime('%H:%M')}.")
            print("Số đo ngoài khe bị nhiễu bởi nhóm khác nên không dùng được.")
            print("Đợi đúng khe, hoặc đo trên cấu hình L trước rồi quay lại.")
            return 3

    levels = CONCURRENCY[profile]
    print(f"ĐO NĂNG LỰC PHỤC VỤ · {settings.profile_banner()}")
    if settings.cache_mode != "off":
        print("\nCẢNH BÁO: CACHE_MODE khác 'off'. Kết quả sẽ đo tốc độ đọc cache,")
        print("không phải tốc độ suy luận. Chạy lại với: CACHE_MODE=off\n")

    rows: list[dict[str, Any]] = []
    for level in levels:
        print(f"  mức đồng thời {level:>2} … ", end="", flush=True)
        row = measure(level, args.requests)
        rows.append(row)
        if "error" in row:
            print(row["error"])
        else:
            print(f"p50={row['p50_s']}s  p95={row['p95_s']}s  {row['tickets_per_hour']} ticket/giờ")

    print()
    print(f"{'đồng thời':>10} {'p50 (s)':>9} {'p95 (s)':>9} {'ticket/giờ':>12} {'lỗi':>6}")
    for row in rows:
        if "error" in row:
            continue
        print(
            f"{row['concurrency']:>10} {row['p50_s']:>9} {row['p95_s']:>9} "
            f"{row['tickets_per_hour']:>12} {row['failures']:>6}"
        )

    print()
    print("KẾT LUẬN CHỌN CẤU HÌNH THAM CHIẾU (SPEC-INFRA-02):")
    print(f"  {decide_reference_profile(rows, args.vram)}")
    print()
    print("Ghi kết luận và số liệu này vào Mục 17 của PROJECT-SPEC.md, và đặt")
    print("CONFIG_PROFILE tương ứng làm mặc định trong .env.example.")

    payload = {
        "measured_at": datetime.now().isoformat(),
        "config_profile": profile,
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
        "cache_mode": settings.cache_mode,
        "team": args.team,
        "slot": args.slot,
        "vram_gb": args.vram,
        "rows": rows,
        "conclusion": decide_reference_profile(rows, args.vram),
    }
    stamp = f"{datetime.now():%Y%m%dT%H%M%S}"
    default_out = ROOT / "eval" / "results" / f"bench-{profile}-{stamp}.json"
    out = Path(args.out) if args.out else default_out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nĐã ghi {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
