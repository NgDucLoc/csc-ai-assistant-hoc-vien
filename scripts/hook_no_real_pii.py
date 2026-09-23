"""Hook pre-commit — chặn số điện thoại Việt Nam có thật lọt vào repo.

SPEC-DATA-01: toàn bộ dữ liệu là dữ liệu sinh tổng hợp. Số thuê bao dùng dải
098700xxxx không tồn tại thực tế.

Đây là hàng rào CUỐI, không phải hàng rào đầu tiên. Trách nhiệm vẫn ở người
soạn dữ liệu. Nhưng hàng rào cuối là thứ khiến khóa học dám công khai repo.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Đầu số di động Việt Nam đang lưu hành.
VN_MOBILE = re.compile(r"\b0(3[2-9]|5[2689]|7[06-9]|8[1-9]|9[0-4-9])\d{7}\b")
ALLOWED = re.compile(r"\b098700\d{4}\b")  # dải giả lập được phép
HOTLINE = {"18008098", "1228", "1414"}


def scan(path: Path) -> list[str]:
    """Tìm số điện thoại có thật trong một tệp."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    findings: list[str] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for match in VN_MOBILE.finditer(line):
            number = match.group(0)
            if ALLOWED.match(number) or number in HOTLINE:
                continue
            findings.append(f"{path}:{i}: {number}")
    return findings


def main(argv: list[str]) -> int:
    """Quét các tệp được truyền vào."""
    findings: list[str] = []
    for name in argv:
        findings.extend(scan(Path(name)))
    if not findings:
        return 0
    print("CHẶN COMMIT — phát hiện số điện thoại có thể là thật (SPEC-DATA-01):")
    for line in findings:
        print(f"  {line}")
    print()
    print("Dữ liệu của khóa học BẮT BUỘC dùng dải giả lập 098700xxxx.")
    print("Nếu đây là số ví dụ trong tài liệu, đổi sang dải trên.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
