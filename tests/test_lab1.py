"""Lab 1 — Canvas, phạm vi, và tính toàn vẹn của bộ dữ liệu.

Lab 1 chưa viết code, nên bộ kiểm thử ở đây kiểm hai thứ khác: tài liệu Canvas
có đủ nội dung bắt buộc chưa, và bộ dữ liệu có đúng cấu trúc và đủ bẫy sư phạm
chưa.

Phần kiểm dữ liệu quan trọng hơn vẻ ngoài của nó. Mỗi bẫy tương ứng với một
nội dung giảng dạy cụ thể; thiếu một bẫy là mất một bài học, và mất lặng lẽ.
"""

from __future__ import annotations

import re
from collections import Counter

import pytest

from src.config import ROOT
from src.data import load_adversarial, load_gold_qa, load_gold_test, load_train
from src.knowledge.governance import conflict_report

pytestmark = pytest.mark.lab1

CATEGORIES = {
    "cuoc_thanh_toan",
    "chat_luong_ket_noi",
    "goi_cuoc_khuyen_mai",
    "thiet_bi_sim",
    "thong_tin_thue_bao",
    "khac",
}
SAFE_SUBSCRIBER = re.compile(r"^098700\d{4}$")


def _section(text: str, title_fragment: str) -> str:
    """Trả về nội dung của mục có tiêu đề chứa ``title_fragment``.

    Tách theo DÒNG tiêu đề, không tách theo chuỗi con: `text.split("## ")` khớp
    nhầm vào bên trong `"### 5.1"` và cắt mục ngay lập tức — lỗi này đã làm bài
    kiểm thử báo sai một lần rồi.
    """
    lines = text.splitlines()
    start = next(
        (i for i, ln in enumerate(lines) if ln.startswith("#") and title_fragment in ln),
        None,
    )
    if start is None:
        return ""
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        if ln.startswith("#") and (len(ln) - len(ln.lstrip("#"))) <= level:
            return "\n".join(lines[start + 1 : j])
    return "\n".join(lines[start + 1 :])


# --- Canvas ----------------------------------------------------------------
def test_canvas_has_seven_cells() -> None:
    """Canvas đủ bảy ô theo yêu cầu deliverable của Session 1."""
    path = ROOT / "docs" / "canvas.md"
    assert path.exists(), "Thiếu docs/canvas.md"
    text = path.read_text(encoding="utf-8")
    for cell in (
        "Vấn đề nghiệp vụ",
        "Người dùng và bối cảnh",
        "Năng lực AI cần có",
        "Dữ liệu và tri thức",
        "Chỉ số thành công",
        "Rủi ro và ranh giới",
        "Phạm vi MVP",
    ):
        assert cell in text, f"Canvas thiếu ô '{cell}'"


def test_canvas_out_of_scope_has_at_least_four_items() -> None:
    """Phần phạm vi KHÔNG làm phải nêu tối thiểu 4 mục cụ thể.

    Đây là điều kiện hoàn thành của Lab 1. Ô này bị bỏ trống hoặc viết chung
    chung là lỗi thường gặp nhất ở Session 1.
    """
    text = (ROOT / "docs" / "canvas.md").read_text(encoding="utf-8")
    block = text.split("NGOÀI phạm vi")[-1].split("\n## ")[0]
    items = [ln for ln in block.splitlines() if ln.strip().startswith(("-", "*"))]
    assert len(items) >= 4, f"Phần NGOÀI phạm vi chỉ có {len(items)} mục, cần tối thiểu 4"


def test_canvas_success_metrics_are_quantified() -> None:
    """Chỉ số thành công phải đo được bằng số, kèm điểm hòa vốn.

    "Tăng sự hài lòng của khách hàng" không phải chỉ số. Bài kiểm thử này ép
    đúng điều giảng viên sẽ yêu cầu sửa ở Session 1.
    """
    text = (ROOT / "docs" / "canvas.md").read_text(encoding="utf-8")
    block = _section(text, "Chỉ số thành công")
    assert block, "Canvas không có mục Chỉ số thành công"
    assert re.search(r"\d+\s*%", block), "Chỉ số thành công thiếu con số phần trăm"
    assert "hòa vốn" in text.lower(), "Canvas thiếu ước lượng điểm hòa vốn"


# --- toàn vẹn dữ liệu ------------------------------------------------------
def test_dataset_sizes_match_spec() -> None:
    """SPEC-DATA-04 — 80 ticket huấn luyện, 40 ticket kiểm định."""
    assert len(load_train()) == 80
    assert len(load_gold_test()) == 40


def test_every_ticket_matches_schema() -> None:
    """SPEC-DATA-02 — mọi ticket đúng lược đồ, không thiếu trường."""
    for row in load_train() + load_gold_test():
        assert row["id"] and row["customer_msg"].strip()
        assert row["channel"] in {"app", "hotline", "email"}
        assert row["label"]["category"] in CATEGORIES
        assert row["label"]["priority"] in {"P1", "P2", "P3"}
        assert row["label"]["sentiment"] in {"trung_tinh", "buc_boi", "gay_gat"}
        assert row["meta"]["expected_action"] in {"auto_draft", "escalate"}


def test_no_real_subscriber_numbers() -> None:
    """SPEC-DATA-01 — số thuê bao thuộc dải giả lập không tồn tại thực tế."""
    for row in load_train() + load_gold_test():
        sub = row.get("subscriber_id")
        if sub:
            assert SAFE_SUBSCRIBER.match(sub), f"{row['id']}: số {sub} ngoài dải giả lập"


def test_all_categories_represented_in_both_sets() -> None:
    """Cả sáu nhóm đều có mặt ở hai tập, nếu không chỉ số theo lớp vô nghĩa."""
    for name, rows in (("train", load_train()), ("gold_test", load_gold_test())):
        present = {r["label"]["category"] for r in rows}
        assert present == CATEGORIES, f"{name} thiếu nhóm: {CATEGORIES - present}"


def test_label_distribution_is_not_degenerate() -> None:
    """Không nhóm nào áp đảo tới mức accuracy trở thành con số vô nghĩa."""
    rows = load_train() + load_gold_test()
    dist = Counter(r["label"]["category"] for r in rows)
    for cat, count in dist.items():
        share = count / len(rows)
        assert share <= 0.35, f"Nhóm {cat} chiếm {share:.0%}, vượt 35%"
        assert share >= 0.04, f"Nhóm {cat} chỉ {share:.0%}, dưới 4%"


@pytest.mark.parametrize(
    ("trap", "expected"),
    [
        ("is_ambiguous", 8),
        ("has_pii", 3),
        ("is_junk", 2),
    ],
)
def test_pedagogical_traps_present_in_exact_counts(trap: str, expected: int) -> None:
    """SPEC-DATA-05 — đếm đủ bẫy sư phạm. Thiếu bẫy là mất một bài học."""
    rows = load_train() + load_gold_test()
    found = sum(1 for r in rows if r["meta"].get(trap))
    assert found == expected, f"Bẫy '{trap}': có {found}, cần đúng {expected}"


def test_ambiguous_tickets_explain_their_label() -> None:
    """Ticket mơ hồ bắt buộc kèm ghi chú lý do gán nhãn.

    Nhãn có lập luận dạy được nhiều hơn nhãn trần, và giảng viên cần lập luận
    đó khi chữa bài.
    """
    for row in load_train() + load_gold_test():
        if row["meta"].get("is_ambiguous"):
            assert row["meta"].get("note", "").strip(), f"{row['id']}: mơ hồ nhưng thiếu ghi chú"


def test_two_conflicting_policy_pairs() -> None:
    """SPEC-DATA-05 — đúng 2 cặp tài liệu chính sách mâu thuẫn."""
    assert len(conflict_report()) == 2


def test_five_unanswerable_questions() -> None:
    """SPEC-DATA-05 — đúng 5 câu hỏi không có đáp án trong kho."""
    rows = load_gold_qa()
    assert sum(1 for r in rows if not r["answerable"]) == 5
    assert sum(1 for r in rows if r["answerable"]) == 40


def test_twelve_adversarial_cases() -> None:
    """SPEC-GUARD-04 — đúng 12 ca đối kháng, phủ đủ các loại tấn công."""
    rows = load_adversarial()
    assert len(rows) == 12
    kinds = {r["kind"] for r in rows}
    assert {"prompt_injection", "data_probing", "money_bait", "out_of_scope", "junk"} <= kinds
