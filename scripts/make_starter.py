"""Sinh bản starter và sáu nhánh cứu hộ từ một nguồn duy nhất.

Chạy:
    uv run python scripts/make_starter.py --lab 3 --out ../starter-lab3
    uv run python scripts/make_starter.py --all --check

**Nguyên tắc NT-1 của kế hoạch xây dựng: viết lời giải đầy đủ trước, bóc ngược
thành starter.** Nguồn sự thật duy nhất là bản solution trong repo này. Bản
starter được sinh tự động bằng cách gỡ các khối mã có đánh dấu.

Viết starter và solution song song bằng tay là cách chắc chắn nhất để hai bản
lệch nhau vào ngày thứ hai của khóa — và khi đó nhánh cứu hộ sẽ đưa cho học
viên một bản mã không khớp với đề bài họ đang làm.

Cú pháp đánh dấu trong mã nguồn::

    # <<LAB-3:CORE>> hint="Điền 5 phần của prompt theo SPEC-PROMPT-01"
    ...mã đầy đủ...
    # <</LAB-3:CORE>>

Khối này trở thành ``raise NotImplementedError`` kèm gợi ý trong bản starter.

.. warning::

   Công cụ đọc từ **cây làm việc hiện tại** (``ROOT``), không đọc từ Git. Khi
   sinh nhiều trạng thái để tạo sáu nhánh cứu hộ, phải sinh **hết cả sáu vào
   thư mục riêng TRƯỚC**, rồi mới lần lượt ghi đè cây làm việc. Vừa sinh vừa
   ghi đè sẽ khiến trạng thái thứ hai trở đi đọc phải bản ĐÃ BỊ GỠ của trạng
   thái trước — nhánh ``solution/session-3`` sẽ không có lời giải Lab 3.

   Lỗi này đã xảy ra một lần và chỉ bị bắt bởi job matrix kiểm nhánh cứu hộ
   trên CI. Đó chính là lý do job đó tồn tại.
"""

from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OPEN = re.compile(r"^(\s*)#\s*<<LAB-(\d):CORE>>\s*(?:hint=\"([^\"]*)\")?\s*$")
CLOSE = re.compile(r"^\s*#\s*<</LAB-(\d):CORE>>\s*$")

# Những gì KHÔNG bao giờ bị gỡ khỏi bản starter. Học viên cần dữ liệu, bộ kiểm
# thử và tài liệu ngay từ đầu — test là đặc tả của bài, không phải đáp án.
#
# `scripts/make_starter.py` tự loại chính mình: docstring của nó chứa VÍ DỤ về
# cú pháp đánh dấu, và ví dụ đó khớp biểu thức chính quy. Không loại thì công
# cụ sẽ gỡ ví dụ trong tài liệu của chính nó — đúng một khối thừa mỗi lần chạy.
NEVER_STRIP = (
    "tests/",
    "data/",
    "docs/",
    "labs/",
    "workbooks/",
    "tai-lieu-bien-soan/",
    "tai-lieu-hoc-vien/",
    ".github/",
    "scripts/make_starter.py",
)

# Thư mục không bao giờ sao chép sang bản starter.
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}

# Chỉ những nhánh đường dẫn này được đưa vào bản starter.
KEEP_PREFIXES = (
    "src/",
    "tests/",
    "data/",
    "docs/",
    "labs/",
    "workbooks/",
    "tai-lieu-bien-soan/",
    "tai-lieu-hoc-vien/",
    "scripts/",
    "eval/",
    ".cache/",
    ".github/",
    "models/",
)

COPY_ALWAYS = [
    "pyproject.toml",
    "uv.lock",
    ".python-version",
    ".env.example",
    ".pre-commit-config.yaml",
    ".gitignore",
    "promptfooconfig.yaml",
    "docker-compose.yml",
    "Dockerfile",
    "README.md",
    "SETUP.md",
    "CHALLENGE.md",
    # Hai tệp này đi cùng MỌI trạng thái repo. PROJECT-SPEC.md nằm ở gốc theo
    # đúng SPEC-ARCH-03; HANDOFF.md là thứ người tiếp nhận đọc đầu tiên.
    "PROJECT-SPEC.md",
    "HANDOFF.md",
]


@dataclass
class Block:
    """Một khối mã được đánh dấu."""

    lab: int
    hint: str
    start: int
    end: int
    indent: str


def find_blocks(lines: list[str]) -> list[Block]:
    """Tìm mọi khối ``<<LAB-N:CORE>>`` trong một tệp.

    Raises:
        ValueError: Khối mở mà không đóng, hoặc lồng nhau.
    """
    blocks: list[Block] = []
    open_at: tuple[int, int, str, str] | None = None

    for i, line in enumerate(lines):
        if (m := OPEN.match(line)) is not None:
            if open_at is not None:
                raise ValueError(f"dòng {i + 1}: khối LAB lồng nhau, không hỗ trợ")
            open_at = (i, int(m.group(2)), m.group(3) or "", m.group(1))
        elif (m := CLOSE.match(line)) is not None:
            if open_at is None:
                raise ValueError(f"dòng {i + 1}: đóng khối mà chưa mở")
            start, lab, hint, indent = open_at
            if lab != int(m.group(1)):
                raise ValueError(f"dòng {i + 1}: đóng LAB-{m.group(1)} nhưng đang mở LAB-{lab}")
            blocks.append(Block(lab=lab, hint=hint, start=start, end=i, indent=indent))
            open_at = None

    if open_at is not None:
        raise ValueError(f"dòng {open_at[0] + 1}: khối LAB-{open_at[1]} không được đóng")
    return blocks


def strip_file(text: str, up_to_lab: int) -> tuple[str, int]:
    """Gỡ các khối thuộc lab > ``up_to_lab``.

    Bản starter của Lab N chứa đầy đủ lời giải của các lab trước — đó chính là
    cách nhánh cứu hộ hoạt động: nhóm tụt lại nhận trạng thái đúng sau buổi
    trước rồi làm tiếp buổi hiện tại.

    Returns:
        Cặp (nội dung mới, số khối đã gỡ).
    """
    lines = text.splitlines()
    blocks = [b for b in find_blocks(lines) if b.lab > up_to_lab]
    if not blocks:
        return text, 0

    out: list[str] = []
    cursor = 0
    for block in blocks:
        out.extend(lines[cursor : block.start])
        pad = block.indent
        todo_hint = block.hint or "Hoàn thiện phần này theo hướng dẫn trong labs/"
        out.append(f"{pad}# TODO(LAB-{block.lab}): {todo_hint}")
        out.append(f'{pad}#   Chạy "uv run pytest -m lab{block.lab}" để biết mình đã đúng chưa.')
        out.append(f'{pad}raise NotImplementedError("LAB-{block.lab}: {todo_hint}")')
        cursor = block.end + 1
    out.extend(lines[cursor:])
    return "\n".join(out) + "\n", len(blocks)


def build_starter(up_to_lab: int, out_dir: Path, *, dry_run: bool = False) -> dict[str, int]:
    """Dựng một cây thư mục starter cho lab chỉ định."""
    stats = {"files": 0, "stripped_blocks": 0, "stripped_files": 0}

    if not dry_run:
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)

    for rel in COPY_ALWAYS:
        src = ROOT / rel
        if src.exists() and not dry_run:
            shutil.copy2(src, out_dir / rel)

    for src in sorted(ROOT.rglob("*")):
        if src.is_dir() or any(part in SKIP_DIRS for part in src.parts):
            continue
        rel = src.relative_to(ROOT)
        rel_str = str(rel)
        if rel_str in COPY_ALWAYS or rel_str.startswith(("eval/results/", "eval/mlruns/", "logs/")):
            continue
        if not rel_str.startswith(KEEP_PREFIXES):
            continue

        dst = out_dir / rel
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)

        stats["files"] += 1
        if src.suffix != ".py" or rel_str.startswith(NEVER_STRIP):
            if not dry_run:
                shutil.copy2(src, dst)
            continue

        text = src.read_text(encoding="utf-8")
        new_text, removed = strip_file(text, up_to_lab)
        if removed:
            stats["stripped_blocks"] += removed
            stats["stripped_files"] += 1
        if not dry_run:
            dst.write_text(new_text, encoding="utf-8")

    return stats


def check_markers() -> int:
    """Kiểm tra mọi đánh dấu trong repo đều cân đối.

    Chạy trong CI. Một khối mở mà không đóng làm bản starter sinh ra sai lệch,
    và lỗi đó chỉ lộ ra khi đã phát cho học viên.
    """
    problems: list[str] = []
    counts: dict[int, int] = {}

    scanned = sorted([*(ROOT / "src").rglob("*.py"), *(ROOT / "eval").rglob("*.py")])
    for path in scanned:
        try:
            blocks = find_blocks(path.read_text(encoding="utf-8").splitlines())
        except ValueError as exc:
            problems.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        for block in blocks:
            counts[block.lab] = counts.get(block.lab, 0) + 1
            if not block.hint:
                problems.append(
                    f"{path.relative_to(ROOT)}:{block.start + 1}: " f"khối LAB-{block.lab} thiếu hint="
                )

    print("Đánh dấu khối theo lab:")
    for lab in sorted(counts):
        print(f"  LAB-{lab}: {counts[lab]} khối")
    if not counts:
        print("  (chưa đánh dấu khối nào — bản solution hiện là bản đầy đủ)")

    if problems:
        print("\nLỖI:")
        for p in problems:
            print(f"  {p}")
        return 1
    print("\nMọi đánh dấu cân đối.")

    # Chốt chặn: bản sinh phải chứa ĐÚNG danh sách tệp Git đang theo dõi.
    # Thiếu một thư mục trong KEEP_PREFIXES là lỗi im lặng — nhánh cứu hộ vẫn
    # tạo được, chỉ là học viên nhận thiếu tài liệu và không ai biết ngay.
    import subprocess

    # -z và core.quotepath=false: tên tệp có dấu cách và có dấu tiếng Việt sẽ
    # bị `git ls-files` mặc định bọc nháy và escape, tách theo khoảng trắng là vỡ.
    tracked = [
        f
        for f in subprocess.run(
            ["git", "-c", "core.quotepath=false", "ls-files", "-z"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.split("\0")
        if f
    ]
    covered = [f for f in tracked if f in COPY_ALWAYS or f.startswith(KEEP_PREFIXES)]
    uncovered = sorted(set(tracked) - set(covered))
    if uncovered:
        print(f"\nLỖI: {len(uncovered)} tệp Git theo dõi nhưng KHÔNG được sao chép sang starter:")
        for f in uncovered[:20]:
            print(f"  {f}")
        print("\nBổ sung tiền tố vào KEEP_PREFIXES hoặc tên tệp vào COPY_ALWAYS.")
        return 1
    print(f"Bản sinh phủ đủ {len(tracked)} tệp Git đang theo dõi.")
    return 0


def main() -> int:
    """Sinh starter hoặc kiểm tra đánh dấu."""
    ap = argparse.ArgumentParser(description="Sinh bản starter từ bản solution")
    ap.add_argument(
        "--lab", type=int, choices=range(0, 7), help="Sinh bản STARTER cho lab này — trạng thái ĐẦU buổi N"
    )
    ap.add_argument(
        "--solution",
        type=int,
        choices=range(1, 7),
        help="Sinh bản SOLUTION sau buổi N — trạng thái CUỐI buổi N, "
        "dùng cho nhánh cứu hộ solution/session-N",
    )
    ap.add_argument("--all", action="store_true", help="Sinh cả sáu bản")
    ap.add_argument("--out", default=None, help="Thư mục đích")
    ap.add_argument("--check", action="store_true", help="Chỉ kiểm tra đánh dấu, không sinh")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.check or not (args.lab is not None or args.solution is not None or args.all):
        return check_markers()

    # Hai trạng thái khác nhau, đừng lẫn:
    #   --lab N       trạng thái ĐẦU buổi N. Lab N chưa làm, lab trước đã xong.
    #   --solution N  trạng thái CUỐI buổi N. Lab N đã xong. Đây là nhánh cứu hộ.
    if args.solution is not None:
        targets = [args.solution]
        up_to = {args.solution: args.solution}
        label = "Solution sau buổi"
    else:
        targets = list(range(1, 7)) if args.all else [args.lab]
        up_to = {n: n - 1 for n in targets}
        label = "Starter đầu buổi"

    base = Path(args.out) if args.out else ROOT.parent / "csc-starters"

    for lab in targets:
        out_dir = base / f"starter-lab{lab}" if args.all else base
        stats = build_starter(up_to[lab], out_dir, dry_run=args.dry_run)
        print(f"{label} {lab} → {out_dir}")
        print(
            f"    {stats['files']} tệp, gỡ {stats['stripped_blocks']} khối "
            f"trong {stats['stripped_files']} tệp"
        )

    print()
    print("Bước tiếp theo — tạo nhánh cứu hộ tương ứng:")
    print("    git checkout -b solution/session-N && git push -u origin solution/session-N")
    print()
    print("Nhớ: CI có job matrix chạy trên cả sáu nhánh cứu hộ. Nhánh cứu hộ không")
    print("được kiểm thử là nhánh cứu hộ hỏng, và nó sẽ hỏng đúng lúc một nhóm cần dùng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
