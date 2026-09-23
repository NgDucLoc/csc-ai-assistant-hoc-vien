"""Chấm tự động phần định lượng của thang điểm — công cụ vận hành nhịp ba ngày.

Chạy: uv run python scripts/grade.py 3 --team nhom-a

Năm bài nộp dồn vào ba tối, trong đó hai tối phải chấm hai bài. Sáu nhóm × 2
bài × 2 tối là khối lượng không chấm tay kịp.

Script này chấm **phần định lượng**: test xanh, đủ số ADR đúng mẫu, đủ bảy ô
canvas, chỉ số đạt ngưỡng, 12/12 ca đối kháng. Giảng viên chỉ chấm phần định
tính là chất lượng lập luận và quyết định thiết kế — phần mà máy không chấm
được và cũng không nên chấm.

Thang điểm lấy từ mục D của từng session trong kế hoạch nội dung buổi học.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@dataclass
class Criterion:
    """Một tiêu chí chấm điểm."""

    name: str
    max_points: float
    auto: bool
    earned: float = 0.0
    note: str = ""


@dataclass
class Rubric:
    """Phiếu chấm của một lab."""

    lab: int
    title: str
    criteria: list[Criterion] = field(default_factory=list)

    @property
    def auto_total(self) -> float:
        """Tổng điểm phần chấm tự động."""
        return sum(c.earned for c in self.criteria if c.auto)

    @property
    def auto_max(self) -> float:
        """Điểm tối đa của phần chấm tự động."""
        return sum(c.max_points for c in self.criteria if c.auto)

    @property
    def manual_max(self) -> float:
        """Điểm tối đa của phần giảng viên chấm tay."""
        return sum(c.max_points for c in self.criteria if not c.auto)


def _pytest_passes(marker: str) -> tuple[bool, str]:
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-m", marker, "--no-header"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tail = [ln for ln in out.stdout.strip().splitlines() if ln.strip()]
    return out.returncode == 0, tail[-1] if tail else ""


def _read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _latest_eval() -> dict | None:
    results = sorted((ROOT / "eval" / "results").glob("eval-*.json"))
    if not results:
        return None
    return json.loads(results[-1].read_text(encoding="utf-8"))


# --- phiếu chấm từng lab ---------------------------------------------------
def rubric_lab1() -> Rubric:
    """Session 1 — thang 10."""
    r = Rubric(1, "AI Opportunity Canvas")
    canvas = _read("docs/canvas.md")
    cells = [
        "Vấn đề nghiệp vụ",
        "Người dùng và bối cảnh",
        "Năng lực AI cần có",
        "Dữ liệu và tri thức",
        "Chỉ số thành công",
        "Rủi ro và ranh giới",
        "Phạm vi MVP",
    ]

    c1 = Criterion("Sơ đồ quy trình phản ánh đúng nghiệp vụ", 2, auto=False)
    c2 = Criterion("Bảng chấm điểm có lập luận rõ ràng", 2, auto=False)

    have = sum(1 for cell in cells if cell in canvas)
    block = canvas.split("NGOÀI phạm vi")[-1].split("\n## ")[0]
    out_items = len([ln for ln in block.splitlines() if ln.strip().startswith(("-", "*"))])
    c3 = Criterion("Canvas đủ 7 ô, phạm vi KHÔNG làm >= 4 mục", 3, auto=True)
    c3.earned = (2.0 if have == 7 else 2.0 * have / 7) + (1.0 if out_items >= 4 else 0.0)
    c3.note = f"{have}/7 ô, {out_items} mục ngoài phạm vi"

    c4 = Criterion("Chỉ số đo được bằng số, có điểm hòa vốn", 2, auto=True)
    has_pct = bool(re.search(r"\d+\s*%", canvas))
    has_be = "hòa vốn" in canvas.lower()
    c4.earned = (1.0 if has_pct else 0.0) + (1.0 if has_be else 0.0)
    c4.note = f"chỉ số định lượng={'có' if has_pct else 'thiếu'}, điểm hòa vốn={'có' if has_be else 'thiếu'}"

    c5 = Criterion("Trình bày mạch lạc, trả lời được phản biện", 1, auto=False)
    r.criteria = [c1, c2, c3, c4, c5]
    return r


def rubric_lab2() -> Rubric:
    """Session 2 — thang 10."""
    r = Rubric(2, "AI Solution Blueprint")
    blueprint = _read("docs/blueprint.md")
    adrs = sorted((ROOT / "docs" / "adr").glob("0*.md"))

    c1 = Criterion("Sơ đồ kiến trúc đủ 5 tầng", 3, auto=True)
    layers = sum(1 for i in range(1, 6) if f"Tầng {i}" in blueprint)
    c1.earned = 3.0 * layers / 5
    c1.note = f"{layers}/5 tầng"

    c2 = Criterion("Mỗi thành phần có phương án dự phòng", 2, auto=False)

    c3 = Criterion("Tối thiểu 5 ADR đúng mẫu bốn phần", 3, auto=True)
    required = ["## Bối cảnh", "## Các phương án đã cân nhắc", "## Quyết định", "## Hệ quả chấp nhận"]
    valid = sum(1 for p in adrs if all(part in p.read_text(encoding="utf-8") for part in required))
    c3.earned = min(3.0, 3.0 * valid / 5)
    c3.note = f"{valid}/{len(adrs)} ADR đúng mẫu"

    c4 = Criterion("Khung khởi động được, CI xanh", 2, auto=True)
    ok, detail = _pytest_passes("lab2")
    c4.earned = 2.0 if ok else 0.0
    c4.note = detail
    r.criteria = [c1, c2, c3, c4]
    return r


def rubric_lab3() -> Rubric:
    """Session 3 — thang 10."""
    r = Rubric(3, "Context Specification")
    spec = _read("docs/context_spec.md")
    prompts = list((ROOT / "src" / "agent" / "prompts").glob("*.v*.md"))

    c1 = Criterion("Prompt đủ 5 phần, lưu thành tệp có phiên bản", 2, auto=True)
    c1.earned = 2.0 if len(prompts) >= 2 else 1.0 if prompts else 0.0
    c1.note = f"{len(prompts)} tệp prompt có đánh số phiên bản"

    c2 = Criterion("Xác thực và thử lại hoạt động, có số liệu trước sau", 2, auto=True)
    ok, detail = _pytest_passes("lab3")
    has_numbers = bool(re.search(r"\d+\s*%|\d\.\d{2}", spec))
    c2.earned = (1.0 if ok else 0.0) + (1.0 if has_numbers else 0.0)
    c2.note = f"{detail}; số liệu trong context_spec={'có' if has_numbers else 'thiếu'}"

    c3 = Criterion("Kho tri thức dựng được, truy hồi đúng chủ đề", 2, auto=True)
    c3.earned = 2.0 if ok else 0.0

    c4 = Criterion("Hai thí nghiệm có số đo, một bảng so sánh prompt", 2, auto=True)
    has_table = spec.count("|") >= 12
    c4.earned = 2.0 if (has_table and has_numbers) else 1.0 if has_table else 0.0
    c4.note = f"bảng kết quả={'có' if has_table else 'thiếu'}"

    c5 = Criterion("Tài liệu giải thích được lý do lựa chọn", 2, auto=False)
    r.criteria = [c1, c2, c3, c4, c5]
    return r


def rubric_lab4() -> Rubric:
    """Session 4 — thang 10."""
    r = Rubric(4, "AI Prototype v1")
    ok, detail = _pytest_passes("lab4")

    c1 = Criterion("Quy trình chạy thông trên ticket thử nghiệm", 3, auto=True)
    c1.earned = 3.0 if ok else 0.0
    c1.note = detail

    c2 = Criterion("Gọi công cụ hoạt động, có đường dự phòng theo luật", 2, auto=True)
    c2.earned = 2.0 if ok else 0.0

    c3 = Criterion("Tối thiểu 4 điều kiện chuyển người, đã kiểm chứng", 2, auto=True)
    try:
        from src.agent.workflow import EscalationReason

        n = len(list(EscalationReason))
        c3.earned = 2.0 if n >= 4 else 0.5 * n
        c3.note = f"{n} điều kiện"
    except Exception as exc:  # noqa: BLE001
        c3.note = str(exc)[:60]

    c4 = Criterion("Màn hình duyệt ghi được nhật ký thao tác", 2, auto=True)
    c4.earned = 2.0 if (ROOT / "src" / "ui" / "app.py").exists() and ok else 0.0

    c5 = Criterion("Video trình diễn đủ ba tình huống", 1, auto=False)
    r.criteria = [c1, c2, c3, c4, c5]
    return r


def rubric_lab5() -> Rubric:
    """Session 5 — thang 10."""
    r = Rubric(5, "Production-ready Prototype")
    report = _latest_eval()
    evaluation = _read("docs/EVALUATION.md")

    c1 = Criterion("Hệ thống bất đồng bộ, đóng gói khởi động từ máy sạch", 2, auto=True)
    c1.earned = 2.0 if (ROOT / "docker-compose.yml").exists() and (ROOT / "src/api/main.py").exists() else 0.0

    c2 = Criterion("Đủ 5 nhóm chỉ số, ghi được vào MLflow", 3, auto=True)
    if report:
        groups = sum(1 for key in ("classification", "retrieval", "adversarial") if report.get(key)) + sum(
            1
            for key in ("generation", "operational", "safety")
            if (report.get("classification") or {}).get(key)
        )
        c2.earned = min(3.0, 3.0 * groups / 6)
        c2.note = f"{groups}/6 nhóm chỉ số; mlflow_run={report.get('mlflow_run_id') or 'không có'}"
        if not report.get("manifest", {}).get("config_profile"):
            c2.earned = 0.0
            c2.note += " — THIẾU config_profile trong manifest, số liệu không so sánh được"
    else:
        c2.note = "chưa có kết quả trong eval/results/"

    c3 = Criterion("Phân tích lỗi chỉ ra nguyên nhân, không chỉ liệt kê số", 2, auto=False)

    c4 = Criterion("Guardrails vượt toàn bộ 12 ca đối kháng", 2, auto=True)
    if report and (adv := report.get("adversarial")):
        c4.earned = 2.0 * (adv.get("passed", 0) / max(1, adv.get("total", 12)))
        c4.note = f"{adv.get('passed')}/{adv.get('total')}"

    c5 = Criterion("Truy vết được ticket bất kỳ, CI có cổng chất lượng", 1, auto=True)
    ok, _ = _pytest_passes("lab5")
    has_profile_col = "cấu hình" in evaluation.lower()
    c5.earned = (0.5 if ok else 0.0) + (0.5 if has_profile_col else 0.0)
    c5.note = f"bảng số liệu ghi cấu hình={'có' if has_profile_col else 'THIẾU'}"
    r.criteria = [c1, c2, c3, c4, c5]
    return r


def rubric_lab6() -> Rubric:
    """Session 6 — thang 10."""
    r = Rubric(6, "Final AI Application")
    card = _read("docs/MODEL_CARD.md")

    c1 = Criterion("Hai cải tiến đo lại đúng phương pháp", 2, auto=False)

    c2 = Criterion("Model Card đầy đủ, có kiểm tra thiên lệch", 2, auto=True)
    has_limits = "giới hạn" in card.lower()
    has_bias = "thiên lệch" in card.lower()
    c2.earned = (1.0 if has_limits else 0.0) + (1.0 if has_bias else 0.0)
    c2.note = f"giới hạn={'có' if has_limits else 'thiếu'}, thiên lệch={'có' if has_bias else 'thiếu'}"

    c3 = Criterion("Trình diễn đủ bốn tình huống", 2, auto=False)
    c4 = Criterion("Bảo vệ được quyết định thiết kế", 2, auto=False)

    c5 = Criterion("Gói bàn giao đủ để đơn vị vận hành tiếp nhận", 2, auto=True)
    parts = ["docs/handover/RUNBOOK.md", "docs/handover/INCIDENTS.md", "docs/handover/RESPONSIBILITIES.md"]
    have = sum(1 for p in parts if (ROOT / p).exists())
    c5.earned = 2.0 * have / len(parts)
    c5.note = f"{have}/{len(parts)} tài liệu bàn giao"
    r.criteria = [c1, c2, c3, c4, c5]
    return r


RUBRICS = {1: rubric_lab1, 2: rubric_lab2, 3: rubric_lab3, 4: rubric_lab4, 5: rubric_lab5, 6: rubric_lab6}


def main() -> int:
    """Chấm một lab và in phiếu điểm."""
    ap = argparse.ArgumentParser(description="Chấm tự động phần định lượng")
    ap.add_argument("lab", type=int, choices=sorted(RUBRICS))
    ap.add_argument("--team", default="")
    ap.add_argument("--json", action="store_true", help="Xuất JSON thay vì bảng")
    args = ap.parse_args()

    r = RUBRICS[args.lab]()

    if args.json:
        print(
            json.dumps(
                {
                    "lab": r.lab,
                    "team": args.team,
                    "title": r.title,
                    "auto_score": round(r.auto_total, 2),
                    "auto_max": r.auto_max,
                    "manual_max": r.manual_max,
                    "criteria": [
                        {
                            "name": c.name,
                            "max": c.max_points,
                            "auto": c.auto,
                            "earned": round(c.earned, 2) if c.auto else None,
                            "note": c.note,
                        }
                        for c in r.criteria
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(f"PHIẾU CHẤM · Lab {r.lab} — {r.title}" + (f" · nhóm {args.team}" if args.team else ""))
    print("=" * 76)
    width = max(len(c.name) for c in r.criteria)
    for c in r.criteria:
        if c.auto:
            print(f"  {c.name:<{width}}  {c.earned:>4.1f}/{c.max_points:<4}  {c.note}")
        else:
            print(f"  {c.name:<{width}}   ——/{c.max_points:<4}  (giảng viên chấm)")
    print("-" * 76)
    print(f"  Phần chấm tự động: {r.auto_total:.1f}/{r.auto_max:.0f}")
    print(f"  Phần chấm tay còn lại: {r.manual_max:.0f} điểm")
    print()
    print("Giảng viên chỉ cần chấm phần định tính: chất lượng lập luận và")
    print("quyết định thiết kế. Đó là phần máy không chấm được và cũng không nên chấm.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
