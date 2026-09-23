"""Dựng chỉ mục vector từ kho tri thức — SPEC-RAG-01.

Chạy:
    uv run python scripts/build_index.py
    uv run python scripts/build_index.py --out data/index_prebuilt

Mất khoảng 2–4 phút trên CPU cho ~300 đoạn. Vì lý do đó bản dựng sẵn ở
``data/index_prebuilt/`` là mặc định của lớp học, còn lệnh này để học viên xác
minh mình dựng lại được — và để giảng viên tạo bản dựng sẵn ở mốc T−1 tuần.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings  # noqa: E402
from src.knowledge.indexer import build_index  # noqa: E402


def main() -> int:
    """Dựng chỉ mục và in bản tóm tắt."""
    ap = argparse.ArgumentParser(description="Dựng chỉ mục tri thức")
    ap.add_argument("--out", default=None, help="Thư mục đích, mặc định theo CHROMA_PATH")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    print(f"Dựng chỉ mục · {settings.profile_banner()}")
    summary = build_index(out_path=args.out, verbose=not args.quiet)
    print()
    for key, value in summary.items():
        print(f"  {key:<16} {value}")
    print()
    print("Sửa bất kỳ tài liệu nào trong data/knowledge/ thì BẮT BUỘC dựng lại chỉ mục")
    print("trong cùng một PR. Chỉ mục lệch với kho tri thức là một lỗi im lặng:")
    print("truy hồi vẫn trả về kết quả, chỉ là kết quả sai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
