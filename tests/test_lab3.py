"""Lab 3 — prompt, đầu ra có cấu trúc, kho tri thức, truy hồi.

Trọng tâm của bộ kiểm thử này là **bốn lớp phòng vệ đầu ra**. Model 3 tỉ tham
số chắc chắn trả về sai định dạng ở một số ca; các bài kiểm thử dưới đây mô
phỏng đúng những kiểu hỏng thường gặp và đòi hỏi hệ thống vẫn cho ra kết quả
dùng được.
"""

from __future__ import annotations

import pytest

from src.agent.classifier import classify
from src.agent.loader import list_prompts, load_prompt, validate_structure
from src.config import settings
from src.context.assemble import assemble_context
from src.knowledge.embedding import embed_chunks
from src.knowledge.governance import conflict_report, load_documents
from src.knowledge.preparation import Chunk, build_chunks, chunk_document
from src.llm.schema import (
    CLASSIFICATION_FALLBACK,
    CLASSIFICATION_SCHEMA,
    extract_json,
    parse_with_retry,
    validate,
)
from src.retrieval.filters import filter_hits, judge_evidence
from src.retrieval.models import Hit
from src.retrieval.pipeline import Retriever
from src.retrieval.search import cosine, hybrid_search

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


# --- embedding -------------------------------------------------------------
class _FakeEmbedClient:
    """Model embedding giả: vector của một đoạn phụ thuộc độ dài văn bản, ghi lại các lô đã nhận."""

    def __init__(self) -> None:
        self.batches: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.batches.append(list(texts))
        return [[float(len(t)), 1.0] for t in texts]


def _chunk(i: int) -> Chunk:
    return Chunk(
        f"KB-999#{i:02d}",
        "KB-999",
        "Tài liệu thử",
        f"Mục {i}",
        "khac",
        "1.0",
        "2026-01-01",
        f"nội dung số {i}",
    )


def test_embed_chunks_batches_and_keeps_order() -> None:
    """Embed — gọi theo lô, vector trả về đúng thứ tự đoạn, dùng văn bản có tiêu đề dẫn đầu."""
    chunks = [_chunk(i) for i in range(5)]
    client = _FakeEmbedClient()
    vectors = embed_chunks(chunks, client, batch_size=2)
    assert [len(b) for b in client.batches] == [2, 2, 1]
    assert client.batches[0][0] == chunks[0].embedding_text()
    assert [v[0] for v in vectors] == [float(len(c.embedding_text())) for c in chunks]


def test_embed_chunks_reports_progress_and_validates() -> None:
    """Embed — báo tiến độ sau mỗi lô, và từ chối khi model trả sai số vector."""
    seen: list[tuple[int, int]] = []
    embed_chunks(
        [_chunk(i) for i in range(3)],
        _FakeEmbedClient(),
        batch_size=2,
        on_progress=lambda d, t: seen.append((d, t)),
    )
    assert seen == [(2, 3), (3, 3)]

    class Broken:
        def embed(self, texts: list[str]) -> list[list[float]]:
            return [[1.0]]

    with pytest.raises(ValueError):
        embed_chunks([_chunk(0), _chunk(1)], Broken(), batch_size=2)
    with pytest.raises(ValueError):
        embed_chunks([_chunk(0)], _FakeEmbedClient(), batch_size=0)


# --- truy hồi --------------------------------------------------------------
def _index_chunks() -> list[dict]:
    def make(i: str, title: str, text: str, vec: list[float]) -> dict:
        return {
            "chunk_id": f"KB-{i}#00",
            "doc_id": f"KB-{i}",
            "doc_title": title,
            "section": "Mục 1",
            "version": "1.0",
            "effective_date": "2026-01-01",
            "category": "cuoc_thanh_toan",
            "text": text,
            "embedding": vec,
        }

    return [
        make("001", "Phí chậm nộp", "phí chậm nộp cước được tính mỗi ngày", [1.0, 0.0]),
        make("002", "Cẩm nang SIM", "hướng dẫn đổi SIM tại cửa hàng", [0.0, 1.0]),
        make("003", "Gói TS149", "cước gói TS149 mỗi tháng", [0.6, 0.8]),
    ]


def test_cosine_of_parallel_and_orthogonal_vectors() -> None:
    """Cosine — vector song song bằng 1, vuông góc bằng 0."""
    assert cosine([1.0, 2.0], [2.0, 4.0]) == pytest.approx(1.0)
    assert cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_keyword_search_without_vector() -> None:
    """Retrieve — không có vector thì dùng keyword, kết quả sắp giảm dần."""
    hits = hybrid_search("phí chậm nộp cước", _index_chunks(), top_k=3)
    assert hits[0].doc_id == "KB-001"
    assert hits == sorted(hits, key=lambda h: h.score, reverse=True)
    assert all(0.0 <= h.score <= 1.0 for h in hits)


def test_semantic_search_ranks_by_vector() -> None:
    """Retrieve — semantic thuần: câu hỏi không chung từ nào vẫn tìm đúng nhờ vector."""
    hits = hybrid_search("zzz", _index_chunks(), query_vector=[0.0, 1.0], top_k=3, hybrid=False)
    assert hits[0].doc_id == "KB-002"
    assert hits[0].score == pytest.approx(1.0)


def test_hybrid_search_mixes_vector_and_keyword() -> None:
    """Retrieve — hybrid: điểm là trọng số vector cộng phần còn lại của keyword."""
    chunks = _index_chunks()
    hits = hybrid_search("phí chậm nộp", chunks, query_vector=[1.0, 0.0], top_k=1, vector_weight=0.75)
    # vector = 1.0, keyword = 1.0 (cả ba từ đều có) => 0.75 * 1 + 0.25 * 1
    assert hits[0].doc_id == "KB-001"
    assert hits[0].score == pytest.approx(1.0)
    only_vector = hybrid_search("phí chậm nộp", chunks, query_vector=[1.0, 0.0], top_k=1, vector_weight=1.0)
    assert only_vector[0].score == pytest.approx(1.0)


def test_search_returns_at_most_top_k() -> None:
    """Retrieve — trả tối đa top_k kết quả."""
    assert len(hybrid_search("cước", _index_chunks(), top_k=2)) == 2


def test_filter_hits_by_category_and_date() -> None:
    """Filter — loại theo nhóm và theo ngày hiệu lực."""
    hits = [
        Hit("a#0", "A", "Tài liệu A", "Mục", "1.0", "2026-01-01", "x", 0.9, "cuoc_thanh_toan"),
        Hit("b#0", "B", "Tài liệu B", "Mục", "1.0", "2026-06-01", "y", 0.8, "thiet_bi_sim"),
    ]
    assert [h.doc_id for h in filter_hits(hits, categories={"thiet_bi_sim"})] == ["B"]
    assert [h.doc_id for h in filter_hits(hits, as_of="2026-03-01")] == ["A"]
    assert filter_hits(hits) == hits


def test_judge_evidence_rules() -> None:
    """Filter — SPEC-RAG-03: không kết quả hoặc điểm dưới ngưỡng thì không đủ căn cứ."""
    ok, reason = judge_evidence([], 0.35)
    assert not ok and "không trả về kết quả" in reason.lower()
    low = [Hit("a#0", "A", "Tài liệu A", "Mục", "1.0", "2026-01-01", "x", 0.2)]
    ok, reason = judge_evidence(low, 0.35)
    assert not ok and "không đủ căn cứ" in reason.lower()
    high = [Hit("a#0", "A", "Tài liệu A", "Mục", "1.0", "2026-01-01", "x", 0.6)]
    assert judge_evidence(high, 0.35)[0] is True
    assert judge_evidence(high, 0.6)[0] is True, "Điểm bằng ngưỡng vẫn đủ căn cứ"


# --- context ---------------------------------------------------------------
def test_assemble_context_format_and_budget() -> None:
    """Assemble — có trích dẫn, đúng thứ tự, không vượt ngân sách và không cắt cụt giữa đoạn."""
    hits = [
        Hit("a#0", "KB-001", "Cước", "Hạn nộp", "1.0", "2026-01-01", "Hạn nộp là ngày 20.", 0.9),
        Hit("b#0", "KB-002", "SIM", "Đổi SIM", "2.1", "2026-02-01", "Đổi SIM tại cửa hàng.", 0.8),
    ]
    block = assemble_context(hits, max_chars=2000)
    assert block.startswith("[KB-001 v1.0, hiệu lực 2026-01-01] Cước — Hạn nộp\nHạn nộp là ngày 20.")
    assert "\n\n[KB-002 v2.1" in block
    first_only = assemble_context(hits, max_chars=len(block.split("\n\n")[0]) + 5)
    assert first_only == block.split("\n\n")[0]
    assert assemble_context(hits, max_chars=10) == ""
    assert assemble_context([], 2000) == ""


# --- pipeline retrieval ----------------------------------------------------
@pytest.fixture(scope="module")
def retriever() -> Retriever:
    """Retriever dùng chỉ mục dựng sẵn (không có thì dựng chỉ mục từ khóa trong bộ nhớ)."""
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
    out = retriever.retrieve("công thức nấu phở bò truyền thống Hà Nội")
    assert not out.grounded
    assert "không đủ căn cứ" in out.reason.lower() or "không trả về kết quả" in out.reason.lower()


def test_retriever_uses_vector_when_index_has_embeddings() -> None:
    """Pipeline — chỉ mục có vector thì nhúng truy vấn và chạy hybrid; model lỗi thì rơi về keyword."""
    r = Retriever(client=_FakeEmbedClient())
    r.chunks = _index_chunks()
    r.has_vectors = True
    out = r.retrieve("phí chậm nộp", query_vector=[1.0, 0.0])
    assert out.mode == "hybrid" and out.hits[0].doc_id == "KB-001"

    class Down:
        def embed(self, texts: list[str]) -> list[list[float]]:
            raise ConnectionError("model embedding không phản hồi")

    r2 = Retriever(client=Down())
    r2.chunks = _index_chunks()
    r2.has_vectors = True
    object.__setattr__(settings, "retrieve_mode", "auto")
    try:
        out2 = r2.retrieve("phí chậm nộp")
    finally:
        object.__setattr__(settings, "retrieve_mode", "keyword")
    assert out2.mode == "keyword" and out2.hits


def test_citation_format_is_traceable(retriever: Retriever) -> None:
    """SPEC-RAG-04 — trích dẫn nêu đủ mã, phiên bản và ngày hiệu lực."""
    hit = retriever.search("bồi thường gián đoạn dịch vụ")[0]
    citation = hit.citation()
    assert citation.startswith("[KB-") and "hiệu lực" in citation and "v" in citation


# --- classify (dùng model qua LLMClient) ----------------------------------
class _FakeLLM:
    """Model ngôn ngữ giả: trả lần lượt các câu trả lời đã định, ghi lại nội dung gửi đi."""

    def __init__(self, replies: list[str]) -> None:
        self.replies = replies
        self.sent: list[str] = []

    def complete(self, *, task: str, system: str, user: str, params: dict | None = None):  # noqa: ANN201
        from types import SimpleNamespace

        self.sent.append(user)
        return SimpleNamespace(text=self.replies[len(self.sent) - 1], from_cache=False)


_GOOD = '{"category": "cuoc_thanh_toan", "priority": "P2", "sentiment": "buc_boi", "confidence": 0.8}'


def test_classify_returns_classification_directly() -> None:
    """classify — model trả JSON đúng thì đi thẳng, lớp direct, gọi model một lần."""
    llm = _FakeLLM([_GOOD])
    result = classify("Tháng này tôi bị trừ tiền lạ.", client=llm)
    assert result.category == "cuoc_thanh_toan"
    assert result.defense_layer == "direct" and result.attempts == 1 and not result.needs_human
    assert "<ticket>" in llm.sent[0] and "Tháng này tôi bị trừ tiền lạ." in llm.sent[0]


def test_classify_retries_with_error_feedback_in_prompt() -> None:
    """classify — lần thử lại phải nhận được thông báo lỗi của lần trước ngay trong prompt."""
    llm = _FakeLLM(["Tôi nghĩ là cước.", _GOOD])
    result = classify("Ticket thử", client=llm)
    assert result.attempts == 2 and result.defense_layer == "retry_1"
    assert "SỬA LỖI" in llm.sent[1] and "SỬA LỖI" not in llm.sent[0]


def test_classify_never_raises_on_garbage() -> None:
    """classify — hỏng hết vẫn không ném lỗi, thành một ca chuyển người."""
    result = classify("Ticket thử", client=_FakeLLM(["rác"] * 3))
    assert result.needs_human and result.defense_layer == "fallback"
    assert result.category == "khac" and result.confidence == 0.0
