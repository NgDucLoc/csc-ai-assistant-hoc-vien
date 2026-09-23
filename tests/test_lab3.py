"""Lab 3 — prompt, đầu ra có cấu trúc, kho tri thức, truy hồi.

Trọng tâm của bộ kiểm thử này là **bốn lớp phòng vệ đầu ra**. Model 3 tỉ tham
số chắc chắn trả về sai định dạng ở một số ca; các bài kiểm thử dưới đây mô
phỏng đúng những kiểu hỏng thường gặp và đòi hỏi hệ thống vẫn cho ra kết quả
dùng được.
"""

from __future__ import annotations

import pytest

from src.agent.loader import list_prompts, load_prompt, validate_structure
from src.config import settings
from src.knowledge.indexer import build_chunks, chunk_document
from src.knowledge.loader import conflict_report, load_documents
from src.knowledge.retriever import Retriever
from src.llm.schema import (
    CLASSIFICATION_FALLBACK,
    CLASSIFICATION_SCHEMA,
    extract_json,
    parse_with_retry,
    validate,
)

pytestmark = pytest.mark.lab3


# --- prompt ----------------------------------------------------------------
def test_all_prompts_have_five_sections() -> None:
    """SPEC-PROMPT-01 — cấu trúc năm phần là bắt buộc, ép bằng kiểm thử."""
    problems: list[str] = []
    for prompt in list_prompts():
        problems.extend(validate_structure(prompt))
    assert not problems, "\n".join(problems)


def test_prompt_versions_are_retained() -> None:
    """SPEC-PROMPT-02 — phiên bản cũ được giữ lại để so sánh.

    Một cải tiến không có bản đối chứng thì không chứng minh được là cải tiến.
    """
    versions = [p.version for p in list_prompts() if p.prompt_id == "classify"]
    assert len(versions) >= 2, "Cần giữ tối thiểu hai phiên bản prompt phân loại"
    assert load_prompt("classify").version == max(versions)


def test_prompt_separates_user_content_with_tags() -> None:
    """SPEC-PROMPT-02 — ngữ cảnh do người dùng cung cấp phải được phân tách.

    Đây là lớp phòng vệ đầu tiên trước chèn lệnh: nội dung ticket nằm giữa thẻ
    đánh dấu và prompt nói rõ đó là dữ liệu, không phải chỉ thị.
    """
    for name in ("classify", "generate"):
        template = load_prompt(name).template
        assert "<ticket>" in template and "</ticket>" in template, f"{name}: thiếu thẻ phân tách"
        assert "không phải chỉ thị" in template or "không phải chỉ thị dành cho bạn" in template


def test_prompt_stays_in_token_budget() -> None:
    """SPEC-INFRA-04 — ngân sách prompt được ép bằng cổng kiểm tra.

    Khi hạ tầng đủ nhanh, kỷ luật tối ưu ngữ cảnh chỉ còn giữ được bằng cổng
    tự động; tốc độ phần cứng không còn ép giúp nữa.
    """
    for prompt in list_prompts():
        assert prompt.estimated_tokens() <= settings.max_system_prompt_tokens, (
            f"{prompt.ref}: {prompt.estimated_tokens()} token, "
            f"vượt ngân sách {settings.max_system_prompt_tokens}"
        )


def test_generate_prompt_forbids_money_commitment() -> None:
    """SPEC-PROMPT-03 — ràng buộc bắt buộc trong prompt sinh phản hồi."""
    template = load_prompt("generate").template
    assert "Không cam kết bồi thường" in template
    assert "KHÔNG ĐỦ CĂN CỨ" in template
    assert "trích dẫn" in template.lower()


# --- lớp phòng vệ đầu ra ---------------------------------------------------
# Cùng một JSON hợp lệ, bọc trong năm kiểu văn bản thừa mà model nhỏ hay sinh ra.
_OK = '{"category": "cuoc_thanh_toan", "priority": "P2", "sentiment": "buc_boi", "confidence": 0.8}'


@pytest.mark.parametrize(
    "raw",
    [
        _OK,
        f"Đây là kết quả phân loại:\n{_OK}",
        f"```json\n{_OK}\n```",
        _OK.replace('"', "'"),
        f"Chắc chắn rồi! {_OK} Hy vọng giúp ích.",
    ],
)
def test_layer2_extracts_json_from_messy_output(raw: str) -> None:
    """Lớp 2 — bóc JSON khỏi năm kiểu văn bản thừa mà model nhỏ hay sinh ra."""
    data = extract_json(raw)
    assert data is not None, f"Không bóc được JSON từ: {raw[:60]}"
    assert data["category"] == "cuoc_thanh_toan"


def test_layer2_returns_none_for_unrecoverable_output() -> None:
    """Lớp 2 — không cứu được thì trả None để lớp 3 vào cuộc, không ném lỗi."""
    assert extract_json("Tôi nghĩ ticket này thuộc nhóm cước, mức ưu tiên trung bình.") is None
    assert extract_json("") is None


def test_layer1_schema_validation_catches_bad_enum() -> None:
    """Lớp 1 — giá trị ngoài danh sách cho phép bị bắt."""
    errors = validate(
        {"category": "billing", "priority": "P2", "sentiment": "buc_boi", "confidence": 0.8},
        CLASSIFICATION_SCHEMA,
    )
    assert any("category" in e for e in errors)


def test_layer1_catches_confidence_out_of_range() -> None:
    """Lớp 1 — độ tin cậy phải nằm trong [0, 1]."""
    errors = validate(
        {"category": "khac", "priority": "P3", "sentiment": "trung_tinh", "confidence": 7},
        CLASSIFICATION_SCHEMA,
    )
    assert any("confidence" in e for e in errors)


def test_layer3_retries_with_error_feedback() -> None:
    """Lớp 3 — thử lại có đưa thông báo lỗi vào prompt.

    Bảo model "sai định dạng, làm lại" hiệu quả hơn nhiều so với gọi lại y hệt.
    Bài kiểm thử ép đúng hành vi đó: lần thứ hai phải nhận được phản hồi lỗi.
    """
    seen: list[str | None] = []
    replies = [
        "Tôi nghĩ đây là vấn đề về cước.",
        '{"category": "cuoc_thanh_toan", "priority": "P2", "sentiment": "buc_boi", "confidence": 0.7}',
    ]

    def call(error: str | None) -> str:
        seen.append(error)
        return replies[len(seen) - 1]

    outcome = parse_with_retry(call, CLASSIFICATION_SCHEMA, CLASSIFICATION_FALLBACK)
    assert outcome.ok
    assert outcome.attempts == 2
    assert outcome.layer == "retry_1"
    assert seen[0] is None and seen[1] is not None, "Lần thử lại phải nhận được thông báo lỗi"


def test_layer4_fallback_marks_needs_human() -> None:
    """Lớp 4 — hỏng hết vẫn không ném lỗi, mà thành một ca chuyển người.

    Đây là chỗ nguyên tắc suy giảm có kiểm soát của SPEC-ARCH-02 được hiện thực.
    """
    outcome = parse_with_retry(lambda _e: "không phải JSON", CLASSIFICATION_SCHEMA, CLASSIFICATION_FALLBACK)
    assert not outcome.ok
    assert outcome.layer == "fallback"
    assert outcome.data["needs_human"] is True
    assert outcome.data["confidence"] == 0.0
    assert len(outcome.errors) == 3, "Phải thử đủ 1 lần đầu + 2 lần lại"


# --- kho tri thức ----------------------------------------------------------
def test_knowledge_base_has_28_documents() -> None:
    """SPEC-DATA-04 — kho tri thức đúng 28 tài liệu."""
    assert len(load_documents(include_superseded=True)) == 28


def test_superseded_documents_are_excluded_by_default() -> None:
    """SPEC-DATA-06 — mặc định không nạp tài liệu đã bị thay thế.

    Nhóm nào bỏ qua trường ``status`` sẽ trích dẫn chính sách hết hiệu lực và
    trả lời khách hàng bằng mức bồi thường sai. Đây là bẫy cài có chủ ý.
    """
    active = load_documents()
    every = load_documents(include_superseded=True)
    assert len(active) < len(every)
    assert all(d.is_active for d in active)
    assert {"KB-007", "KB-010"}.isdisjoint({d.doc_id for d in active})


def test_two_conflicting_document_pairs_exist() -> None:
    """SPEC-DATA-05 — đúng 2 cặp tài liệu mâu thuẫn cũ và mới."""
    pairs = conflict_report()
    assert len(pairs) == 2, f"Cần đúng 2 cặp mâu thuẫn, thấy {len(pairs)}"
    assert {p["new_doc"] for p in pairs} == {"KB-012", "KB-013"}


def test_chunks_carry_citation_metadata() -> None:
    """SPEC-RAG-04 — mỗi đoạn mang đủ dữ liệu để truy ngược về tài liệu gốc."""
    chunks = build_chunks()
    assert chunks, "Không chia được đoạn nào"
    for chunk in chunks[:20]:
        assert chunk.doc_id and chunk.version and chunk.effective_date
        assert chunk.doc_title in chunk.embedding_text(), (
            "Tiêu đề tài liệu phải nằm ở đầu văn bản đem nhúng — thí nghiệm ở "
            "Session 3 bước 4 cho thấy riêng thay đổi này đã nâng Recall@5"
        )


def test_chunking_respects_section_boundaries() -> None:
    """SPEC-RAG-01 — chia đoạn theo cấu trúc mục, không cắt cứng theo ký tự."""
    doc = next(d for d in load_documents() if d.doc_id == "KB-012")
    chunks = chunk_document(doc)
    sections = {c.section for c in chunks}
    assert len(sections) >= 3, "Tài liệu nhiều mục phải cho nhiều đoạn theo mục"
    assert all(len(c.text) <= settings.chunk_size * 1.5 for c in chunks)


# --- truy hồi --------------------------------------------------------------
@pytest.fixture(scope="module")
def retriever() -> Retriever:
    """Retriever dùng chỉ mục dựng sẵn."""
    from src.config import ROOT

    return Retriever(ROOT / "data" / "index_prebuilt")


def test_retriever_returns_hits_with_scores(retriever: Retriever) -> None:
    """SPEC-RAG-02 — trả về top-k kèm điểm tương đồng."""
    hits = retriever.search("phí chậm nộp cước tính bao nhiêu phần trăm")
    assert hits
    assert all(0.0 <= h.score <= 1.0 for h in hits)
    assert hits == sorted(hits, key=lambda h: h.score, reverse=True)


def test_retriever_refuses_when_below_threshold(retriever: Retriever) -> None:
    """SPEC-RAG-03 — dưới ngưỡng thì nói không đủ căn cứ, không đoán.

    Ranh giới an toàn quan trọng nhất của hệ thống. Với bài toán chăm sóc khách
    hàng, một trợ lý bịa ra chính sách gây rủi ro nghiệp vụ nghiêm trọng hơn
    nhiều so với một trợ lý im lặng và chuyển tiếp cho người xử lý.
    """
    out = retriever.retrieve("công thức nấu phở bò truyền thống Hà Nội", min_score=0.35)
    assert not out.grounded
    assert "không đủ căn cứ" in out.reason.lower() or "không trả về kết quả" in out.reason.lower()


def test_citation_format_is_traceable(retriever: Retriever) -> None:
    """SPEC-RAG-04 — trích dẫn nêu đủ mã, phiên bản và ngày hiệu lực."""
    hit = retriever.search("bồi thường gián đoạn dịch vụ")[0]
    citation = hit.citation()
    assert citation.startswith("[KB-") and "hiệu lực" in citation and "v" in citation
