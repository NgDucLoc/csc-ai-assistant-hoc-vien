"""Mốc kiểm tra 5 phút cuối mỗi buổi — công cụ vận hành nhịp ba ngày.

Chạy: uv run python scripts/checkpoint.py 3

Sáu session ghép thành ba ngày, mỗi ngày một buổi sáng và một buổi chiều. Giữa
hai buổi chỉ có giờ nghỉ trưa — nhóm tụt lại ở buổi sáng bước thẳng vào buổi
chiều, không có đêm để bù.

Vì vậy giảng viên phải biết nhóm nào cần cứu hộ **trước giờ nghỉ trưa**, không
phải sau khi buổi chiều đã trôi được nửa tiếng. Mỗi nhóm chạy lệnh này trong 5
phút cuối buổi và báo kết quả; giảng viên chốt danh sách nhóm cần
``scripts/rescue.sh`` ngay tại chỗ.

Điều kiện kiểm tra lấy từ SPEC-TRACE-04 — Definition of Done từng lab.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@dataclass
class Item:
    """Một điều kiện hoàn thành."""

    name: str
    ok: bool
    detail: str = ""


def _pytest(marker: str) -> Item:
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-m", marker, "--no-header", "-x"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tail = [ln for ln in out.stdout.strip().splitlines() if ln.strip()]
    return Item(f"pytest -m {marker}", out.returncode == 0, tail[-1] if tail else "")


def _exists(rel: str, label: str) -> Item:
    return Item(label, (ROOT / rel).exists(), rel)


def _count_files(pattern: str, need: int, label: str) -> Item:
    found = len(list(ROOT.glob(pattern)))
    return Item(label, found >= need, f"{found}/{need}")


def _contains(rel: str, needle: str, label: str) -> Item:
    path = ROOT / rel
    if not path.exists():
        return Item(label, False, f"thiếu {rel}")
    return Item(label, needle.lower() in path.read_text(encoding="utf-8").lower(), rel)


# --- Definition of Done từng lab — SPEC-TRACE-04 --------------------------
def lab0() -> list[Item]:
    """Môi trường dựng được, công cụ báo PASS, pre-commit đã cài."""
    return [
        _exists("uv.lock", "uv.lock được commit"),
        _exists(".git/hooks/pre-commit", "pre-commit đã gắn vào Git"),
        _exists(".env", "Đã tạo .env từ .env.example"),
    ]


def lab1() -> list[Item]:
    """Canvas đủ bảy ô, hai chỉ số định lượng, phạm vi KHÔNG làm >= 4 mục."""
    return [
        _exists("docs/canvas.md", "docs/canvas.md tồn tại"),
        _contains("docs/canvas.md", "hòa vốn", "Canvas có ước lượng điểm hòa vốn"),
        _contains("docs/canvas.md", "NGOÀI phạm vi", "Canvas có phần NGOÀI phạm vi"),
        _pytest("lab1"),
    ]


def lab2() -> list[Item]:
    """Blueprint 5 tầng, >= 5 ADR đúng mẫu, khung chạy được, CI lint xanh."""
    return [
        _exists("docs/blueprint.md", "docs/blueprint.md tồn tại"),
        _count_files("docs/adr/0*.md", 5, "Tối thiểu 5 ADR"),
        _exists(".github/workflows/ci.yml", "CI đã cấu hình"),
        _pytest("lab2"),
    ]


def lab3() -> list[Item]:
    """Prompt 5 phần có phiên bản, kho tri thức dựng được, hai thí nghiệm có số đo."""
    return [
        _exists("docs/context_spec.md", "docs/context_spec.md tồn tại"),
        _count_files("src/agent/prompts/*.v*.md", 2, "Prompt có đánh số phiên bản"),
        _exists("promptfooconfig.yaml", "Cấu hình so sánh prompt"),
        _pytest("lab3"),
    ]


def lab4() -> list[Item]:
    """Chạy thông 5 ticket, >= 4 điều kiện chuyển người, màn hình duyệt ghi log."""
    return [
        _exists("src/agent/workflow.py", "Workflow đã cài đặt"),
        _exists("src/ui/app.py", "Màn hình duyệt đã có"),
        _pytest("lab4"),
    ]


def lab5() -> list[Item]:
    """API bất đồng bộ, 5 nhóm chỉ số, 12/12 đối kháng, truy vết được."""
    return [
        _exists("src/api/main.py", "API bất đồng bộ"),
        _exists("docker-compose.yml", "Cấu hình đóng gói"),
        _exists("docs/EVALUATION.md", "docs/EVALUATION.md tồn tại"),
        _contains("docs/EVALUATION.md", "cấu hình", "Bảng số liệu có ghi cấu hình"),
        _pytest("lab5"),
    ]


def lab6() -> list[Item]:
    """Hai cải tiến có số đo, Model Card, gói bàn giao."""
    return [
        _exists("docs/MODEL_CARD.md", "Model Card"),
        _exists("docs/handover/RUNBOOK.md", "Sổ tay vận hành"),
        _exists("docs/handover/INCIDENTS.md", "Quy trình xử lý sự cố"),
        _contains("docs/MODEL_CARD.md", "giới hạn", "Model Card nêu giới hạn đã biết"),
    ]


LABS: dict[int, tuple[str, Callable[[], list[Item]]]] = {
    0: ("Lab 0 — Chuẩn bị môi trường", lab0),
    1: ("Lab 1 — AI Opportunity Canvas", lab1),
    2: ("Lab 2 — AI Solution Blueprint", lab2),
    3: ("Lab 3 — Context Specification", lab3),
    4: ("Lab 4 — AI Prototype v1", lab4),
    5: ("Lab 5 — Production-ready Prototype", lab5),
    6: ("Lab 6 — Final AI Application", lab6),
}


def main() -> int:
    """Chạy kiểm tra điều kiện hoàn thành của một lab."""
    ap = argparse.ArgumentParser(description="Mốc kiểm tra cuối buổi")
    ap.add_argument("lab", type=int, choices=sorted(LABS))
    ap.add_argument("--team", default="", help="Tên nhóm, để in vào báo cáo")
    args = ap.parse_args()

    title, fn = LABS[args.lab]
    print(f"{title}" + (f"  ·  nhóm {args.team}" if args.team else ""))
    print("=" * 64)

    items = fn()
    width = max(len(i.name) for i in items)
    for item in items:
        print(f"  [{'PASS' if item.ok else 'FAIL'}]  {item.name:<{width}}  {item.detail}")

    failed = [i for i in items if not i.ok]
    print()
    if not failed:
        print("ĐỦ ĐIỀU KIỆN HOÀN THÀNH. Nhóm sẵn sàng vào buổi tiếp theo.")
        return 0

    print(f"THIẾU {len(failed)}/{len(items)} điều kiện.")
    print()
    print("Nếu buổi sắp kết thúc và nhóm không kịp hoàn thành, dùng nhánh cứu hộ:")
    print(f"    ./scripts/rescue.sh {args.lab}")
    print("Lệnh này đồng bộ src/, data/ và .cache/ từ solution/session-N và")
    print("KHÔNG đụng vào docs/ — canvas, blueprint và ADR của nhóm được giữ nguyên.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
