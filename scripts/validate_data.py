"""Kiểm tra bộ dữ liệu trước khi coi là dùng được — SPEC-DATA-01…06.

Chạy: uv run python scripts/validate_data.py

Bốn nhóm kiểm tra:

1. **Lược đồ.** Mọi ticket đúng SPEC-DATA-02, mọi tài liệu tri thức có đủ
   front-matter theo SPEC-DATA-06.
2. **Phân bố nhãn.** Không nhóm nào áp đảo hoặc quá hiếm tới mức chỉ số mất
   ý nghĩa thống kê.
3. **Bẫy sư phạm.** Đếm đủ 5 loại bẫy của SPEC-DATA-05. **Bẫy thiếu là lỗi
   chặn**, vì mỗi bẫy tương ứng với một nội dung giảng dạy: bỏ bẫy là bỏ bài.
4. **An toàn dữ liệu.** Số thuê bao thuộc dải không tồn tại, không có thông
   tin định danh thật.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import load_adversarial, load_gold_qa, load_gold_test, load_train  # noqa: E402
from src.knowledge.loader import conflict_report, load_documents  # noqa: E402

CATEGORIES = {
    "cuoc_thanh_toan",
    "chat_luong_ket_noi",
    "goi_cuoc_khuyen_mai",
    "thiet_bi_sim",
    "thong_tin_thue_bao",
    "khac",
}
PRIORITIES = {"P1", "P2", "P3"}
SENTIMENTS = {"trung_tinh", "buc_boi", "gay_gat"}

# Dải số thuê bao giả lập được phép. Mọi số ngoài dải này là lỗi chặn.
SAFE_SUBSCRIBER = re.compile(r"^098700\d{4}$")

REQUIRED_TRAPS = {
    "tài liệu chính sách mâu thuẫn (cặp)": 2,
    "câu hỏi không có đáp án trong kho": 5,
    "ticket mơ hồ gán được hai nhãn": 8,
    "ticket chứa thông tin cá nhân": 3,
    "ticket rác": 2,
}


class Report:
    """Gom lỗi và cảnh báo, in ra bảng tổng hợp ở cuối."""

    def __init__(self) -> None:
        """Khởi tạo báo cáo rỗng."""
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, msg: str) -> None:
        """Ghi một lỗi chặn."""
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        """Ghi một cảnh báo không chặn."""
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        """Ghi một dòng thông tin."""
        self.info.append(msg)


def check_tickets(rows: list[dict[str, Any]], name: str, expected: int, rep: Report) -> None:
    """Kiểm tra lược đồ và phân bố của một tập ticket."""
    if len(rows) != expected:
        rep.error(f"{name}: có {len(rows)} ticket, cần đúng {expected} (SPEC-DATA-04)")

    ids = Counter(r["id"] for r in rows)
    for dup, count in ids.items():
        if count > 1:
            rep.error(f"{name}: mã ticket trùng {dup} ({count} lần)")

    for row in rows:
        label = row.get("label") or {}
        if label.get("category") not in CATEGORIES:
            rep.error(f"{name}/{row['id']}: nhóm vấn đề không hợp lệ {label.get('category')!r}")
        if label.get("priority") not in PRIORITIES:
            rep.error(f"{name}/{row['id']}: mức ưu tiên không hợp lệ {label.get('priority')!r}")
        if label.get("sentiment") not in SENTIMENTS:
            rep.error(f"{name}/{row['id']}: sắc thái không hợp lệ {label.get('sentiment')!r}")
        if not (row.get("customer_msg") or "").strip():
            rep.error(f"{name}/{row['id']}: nội dung rỗng")

        sub = row.get("subscriber_id")
        if sub and not SAFE_SUBSCRIBER.match(sub):
            rep.error(
                f"{name}/{row['id']}: số thuê bao {sub} nằm ngoài dải giả lập 098700xxxx " "(SPEC-DATA-01)"
            )
        meta = row.get("meta") or {}
        if meta.get("is_ambiguous") and not (meta.get("note") or "").strip():
            rep.error(f"{name}/{row['id']}: ticket mơ hồ nhưng thiếu ghi chú lý do gán nhãn")

    dist = Counter(r["label"]["category"] for r in rows)
    total = len(rows) or 1
    rep.note(f"{name} — phân bố nhóm vấn đề:")
    for cat, count in dist.most_common():
        share = count / total
        rep.note(f"    {cat:<22} {count:>3}  ({share:.0%})")
        if share > 0.35:
            rep.warn(f"{name}: nhóm {cat} chiếm {share:.0%}, vượt 35% — chỉ số dễ bị lệch")
        if share < 0.04:
            rep.warn(f"{name}: nhóm {cat} chỉ {share:.0%}, dưới 4% — quá ít để đo tin cậy")
    for cat in CATEGORIES - set(dist):
        rep.error(f"{name}: không có ticket nào thuộc nhóm {cat}")


def check_knowledge(rep: Report) -> dict[str, int]:
    """Kiểm tra kho tri thức và đếm cặp tài liệu mâu thuẫn."""
    active = load_documents()
    every = load_documents(include_superseded=True)
    rep.note(f"Kho tri thức — {len(every)} tài liệu, {len(active)} còn hiệu lực")

    if len(every) != 28:
        rep.error(f"Kho tri thức có {len(every)} tài liệu, cần đúng 28 (SPEC-DATA-04)")

    ids = Counter(d.doc_id for d in every)
    for doc_id, count in ids.items():
        if count > 1:
            rep.error(f"Mã tài liệu trùng: {doc_id} ({count} lần)")

    known = {d.doc_id for d in every}
    for doc in every:
        if doc.supersedes and doc.supersedes not in known:
            rep.error(f"{doc.doc_id}: supersedes trỏ tới {doc.supersedes} không tồn tại")
        if doc.category not in CATEGORIES:
            rep.error(f"{doc.doc_id}: nhóm {doc.category!r} không thuộc bảng phân loại")
        if len(doc.body) < 500:
            rep.warn(f"{doc.doc_id}: thân tài liệu chỉ {len(doc.body)} ký tự, có thể quá ngắn")

    pairs = conflict_report()
    rep.note(f"Cặp tài liệu cũ–mới: {len(pairs)}")
    for pair in pairs:
        rep.note(
            f"    {pair['old_doc']} v{pair['old_version']} → "
            f"{pair['new_doc']} v{pair['new_version']}  ({pair['title']})"
        )
    return {"pairs": len(pairs)}


def check_gold_qa(rep: Report) -> dict[str, int]:
    """Kiểm tra bộ hỏi–đáp vàng và đếm câu không có đáp án."""
    rows = load_gold_qa()
    if not rows:
        rep.error("Thiếu data/gold_qa.jsonl")
        return {"unanswerable": 0}

    answerable = [r for r in rows if r.get("answerable")]
    unanswerable = [r for r in rows if not r.get("answerable")]
    rep.note(f"Bộ hỏi–đáp vàng — {len(answerable)} câu có đáp án, {len(unanswerable)} câu không có")

    if len(answerable) != 40:
        rep.error(f"Cần đúng 40 cặp hỏi–đáp có đáp án, đang có {len(answerable)}")

    known = {d.doc_id for d in load_documents(include_superseded=True)}
    for row in answerable:
        if not row.get("expected_doc_ids"):
            rep.error(f"{row['qa_id']}: câu có đáp án nhưng thiếu expected_doc_ids")
        for doc_id in row.get("expected_doc_ids", []):
            if doc_id not in known:
                rep.error(f"{row['qa_id']}: trỏ tới tài liệu không tồn tại {doc_id}")
    for row in unanswerable:
        if row.get("expected_doc_ids"):
            rep.error(f"{row['qa_id']}: câu không có đáp án mà vẫn khai expected_doc_ids")

    covered = {d for r in answerable for d in r["expected_doc_ids"]}
    rep.note(f"Số tài liệu được bộ hỏi–đáp phủ: {len(covered)}/28")
    return {"unanswerable": len(unanswerable)}


def check_adversarial(rep: Report) -> None:
    """Kiểm tra bộ ca đối kháng."""
    rows = load_adversarial()
    if len(rows) != 12:
        rep.error(f"Bộ đối kháng có {len(rows)} ca, cần đúng 12 (SPEC-GUARD-04)")
    kinds = Counter(r.get("kind") for r in rows)
    summary = ", ".join(f"{k}×{v}" for k, v in kinds.items())
    rep.note(f"Bộ đối kháng — {len(rows)} ca: {summary}")
    for row in rows:
        if not row.get("must"):
            rep.error(f"{row.get('case_id')}: thiếu điều kiện 'must'")


def check_traps(
    train: list[dict[str, Any]],
    test: list[dict[str, Any]],
    extra: dict[str, int],
    rep: Report,
) -> None:
    """Đếm đủ 5 loại bẫy sư phạm — SPEC-DATA-05. Bẫy thiếu là lỗi chặn."""
    every = train + test
    found = {
        "tài liệu chính sách mâu thuẫn (cặp)": extra.get("pairs", 0),
        "câu hỏi không có đáp án trong kho": extra.get("unanswerable", 0),
        "ticket mơ hồ gán được hai nhãn": sum(1 for r in every if r["meta"].get("is_ambiguous")),
        "ticket chứa thông tin cá nhân": sum(1 for r in every if r["meta"].get("has_pii")),
        "ticket rác": sum(1 for r in every if r["meta"].get("is_junk")),
    }
    rep.note("Bẫy sư phạm (SPEC-DATA-05):")
    for name, need in REQUIRED_TRAPS.items():
        have = found[name]
        mark = "OK " if have == need else "SAI"
        rep.note(f"    [{mark}] {name:<38} {have}/{need}")
        if have != need:
            rep.error(
                f"Bẫy '{name}': có {have}, cần đúng {need}. " "Bẫy thiếu nghĩa là mất một nội dung giảng dạy."
            )


def main() -> int:
    """Chạy toàn bộ kiểm tra và in báo cáo."""
    rep = Report()
    train = load_train()
    try:
        test = load_gold_test()
    except FileNotFoundError as exc:
        rep.warn(f"Bỏ qua tập kiểm định: {exc}")
        test = []

    check_tickets(train, "train", 80, rep)
    if test:
        check_tickets(test, "gold_test", 40, rep)
    kb = check_knowledge(rep)
    qa = check_gold_qa(rep)
    check_adversarial(rep)
    if test:
        check_traps(train, test, {**kb, **qa}, rep)

    print("\n".join(rep.info))
    print()
    for msg in rep.warnings:
        print(f"CẢNH BÁO  {msg}")
    for msg in rep.errors:
        print(f"LỖI       {msg}")

    print()
    if rep.errors:
        print(f"KHÔNG ĐẠT — {len(rep.errors)} lỗi, {len(rep.warnings)} cảnh báo")
        return 1
    print(f"ĐẠT — 0 lỗi, {len(rep.warnings)} cảnh báo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
