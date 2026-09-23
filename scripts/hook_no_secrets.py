"""Hook pre-commit — chặn khóa truy cập bị commit nhầm.

Tình huống thực tế trong lớp: học viên sửa .env rồi vô tình `git add -A`.
Khóa truy cập server dùng chung bị lộ nghĩa là phải cấp lại cho cả lớp giữa buổi.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "khóa dạng OpenAI"),
    (
        re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[=:]\s*['\"][^'\"]{12,}['\"]"),
        "khóa gán trực tiếp trong mã",
    ),
    (re.compile(r"(?i)^LLM_API_KEY\s*=\s*(?!<|ollama|\s*$).{8,}"), "LLM_API_KEY có giá trị thật"),
]
SKIP_NAMES = {".env.example"}


def scan(path: Path) -> list[str]:
    """Tìm dấu hiệu khóa truy cập trong một tệp."""
    if path.name in SKIP_NAMES:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    findings: list[str] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for pattern, label in PATTERNS:
            if pattern.search(line):
                findings.append(f"{path}:{i}: {label}")
    return findings


def main(argv: list[str]) -> int:
    """Quét các tệp được truyền vào."""
    findings: list[str] = []
    for name in argv:
        findings.extend(scan(Path(name)))
    if not findings:
        return 0
    print("CHẶN COMMIT — phát hiện khóa truy cập:")
    for line in findings:
        print(f"  {line}")
    print()
    print("Khóa truy cập chỉ được để trong .env, và .env nằm trong .gitignore.")
    print("Nếu khóa đã bị đẩy lên, báo giảng viên để cấp lại cho cả lớp.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
