"""Nạp dữ liệu ticket — SPEC-DATA-02, SPEC-DATA-04.

Nguồn sự thật của bộ ticket là hai module ``scripts/tickets_*_data.py``: nội
dung viết tay, nhãn gán thủ công, kèm ghi chú lý do cho các ca khó. Tệp JSONL
trong ``data/tickets/`` là bản kết xuất để promptfoo và các công cụ ngoài đọc.

Hàm nạp ở đây ưu tiên JSONL nếu có, và tự dựng từ nguồn nếu chưa kết xuất. Nhờ
vậy bộ kiểm thử chạy được ngay sau khi clone, không cần thêm bước chuẩn bị —
điều này quan trọng vì Lab 0 diễn ra tại nhà, không có giảng viên bên cạnh.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any

from src.config import ROOT

TICKETS_DIR = ROOT / "data" / "tickets"
_SCRIPTS = ROOT / "scripts"

CHANNELS = ["app", "hotline", "email"]
SUBSCRIBERS = [f"098700{i:04d}" for i in range(101, 111)]


def _materialize(cases: list[dict[str, Any]], prefix: str, seed: int) -> list[dict[str, Any]]:
    """Đóng gói danh sách ca thành bản ghi đúng lược đồ SPEC-DATA-02.

    Dùng bộ sinh ngẫu nhiên có hạt cố định, nên mã ticket, kênh và thời điểm
    giống hệt nhau trên mọi máy — điều kiện để kết quả đánh giá so sánh được.
    """
    rng = random.Random(seed)
    out: list[dict[str, Any]] = []
    for i, row in enumerate(cases, start=1):
        sub = row.get("sub")
        if sub is None and rng.random() < 0.75:
            sub = rng.choice(SUBSCRIBERS)
        out.append(
            {
                "id": f"{prefix}-{i:05d}",
                "channel": row.get("channel") or rng.choice(CHANNELS),
                "created_at": (
                    f"2026-0{rng.randint(1, 3)}-{rng.randint(10, 28):02d}"
                    f"T{rng.randint(8, 20):02d}:{rng.randint(0, 59):02d}:00+07:00"
                ),
                "customer_msg": row["msg"].strip(),
                "subscriber_id": sub,
                "attachments": [],
                "label": {
                    "category": row["cat"],
                    "priority": row["pri"],
                    "sentiment": row["sen"],
                },
                "meta": {
                    "is_ambiguous": bool(row.get("ambiguous", False)),
                    "has_pii": bool(row.get("pii", False)),
                    "is_junk": bool(row.get("junk", False)),
                    "expected_action": row.get("action", "auto_draft"),
                    "note": row.get("note", ""),
                },
            }
        )
    return out


def _from_source(module: str, attr: str, prefix: str, seed: int) -> list[dict[str, Any]]:
    if str(_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS))
    mod = __import__(module)
    return _materialize(getattr(mod, attr), prefix, seed)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_train() -> list[dict[str, Any]]:
    """Nạp 80 ticket huấn luyện. Công khai cho học viên từ Lab 3."""
    path = TICKETS_DIR / "train.jsonl"
    if path.exists():
        return _read_jsonl(path)
    return _from_source("tickets_train_data", "TRAIN_CASES", "TK", 42)


def load_gold_test() -> list[dict[str, Any]]:
    """Nạp 40 ticket kiểm định.

    BẮT BUỘC giữ kín tới Lab 5. Nếu học viên nhìn thấy tập này khi tinh chỉnh
    prompt, mọi con số đánh giá ở Lab 5 mất ý nghĩa.

    Raises:
        FileNotFoundError: Tập kiểm định chưa được mở khóa cho lớp.
    """
    path = TICKETS_DIR / "gold_test.jsonl"
    if path.exists():
        return _read_jsonl(path)
    try:
        return _from_source("tickets_test_data", "TEST_CASES", "GT", 77)
    except ImportError as exc:  # pragma: no cover — nhánh khi chưa mở khóa
        raise FileNotFoundError(
            "Tập kiểm định chưa có trong nhánh này. Tập gold_test được giữ kín "
            "tới Lab 5 theo SPEC-DATA-04; giảng viên merge vào sau Session 4."
        ) from exc


def load_gold_qa() -> list[dict[str, Any]]:
    """Nạp 40 cặp hỏi–đáp vàng dùng để đo chất lượng truy hồi."""
    path = ROOT / "data" / "gold_qa.jsonl"
    return _read_jsonl(path) if path.exists() else []


def load_adversarial() -> list[dict[str, Any]]:
    """Nạp 12 ca đối kháng dùng để kiểm thử guardrails ở Lab 5."""
    path = ROOT / "tests" / "adversarial" / "cases.jsonl"
    return _read_jsonl(path) if path.exists() else []


def export_jsonl() -> dict[str, int]:
    """Kết xuất hai tập ticket ra JSONL.

    Bước tùy chọn, chỉ cần khi dùng promptfoo hoặc công cụ ngoài. Bộ kiểm thử
    và quy trình đánh giá đọc thẳng từ nguồn nên không phụ thuộc bước này.
    """
    TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for name, rows in (("train", load_train()), ("gold_test", load_gold_test())):
        target = TICKETS_DIR / f"{name}.jsonl"
        with target.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        counts[name] = len(rows)
    return counts
