# LAB 3 — Context Specification

Session 3 · Sản phẩm: [`docs/context_spec.md`](../docs/context_spec.md) và mã cho 6 khối

Lab 3 xây phần tri thức của ứng dụng: đọc và quản lý tài liệu, chia đoạn, embedding, truy hồi, ghép context, rồi cho model trả lời có căn cứ. Cấu trúc thư mục đi theo đúng sơ đồ slide Session 3: [`src/knowledge/`](../src/knowledge/) (Knowledge Engineering), [`src/retrieval/`](../src/retrieval/) (Retrieval Engineering), [`src/context/`](../src/context/) (Context Engineering).

Ghi chép vào Workbook 3 ([`tai-lieu-hoc-vien/workbooks/WORKBOOK-3.docx`](../tai-lieu-hoc-vien/workbooks/WORKBOOK-3.docx), bản văn bản [`workbooks/WORKBOOK-3.md`](../workbooks/WORKBOOK-3.md)). Đề này nói phải làm gì. Workbook hướng dẫn từng bước, giải thích thuật ngữ, mô tả từng khối code và ghi lại đã đo được gì, vì sao chọn như vậy. Mỗi khối code có một đặc tả riêng trong [`PROJECT-SPEC.md`](../PROJECT-SPEC.md) ([SPEC-RAG-05](../PROJECT-SPEC.md#spec-rag-05) đến 10, [SPEC-CTX-01](../PROJECT-SPEC.md#spec-ctx-01)) để tự viết hoặc giao cho trợ lý AI.

Session 4 dựa thẳng lên phần retrieval làm ở đây. Cuối buổi chạy `scripts/checkpoint.py 3`, thiếu thì dùng `./scripts/rescue.sh 3` ngay.

Công cụ đo của buổi này là [`scripts/lab3_check.py`](../scripts/lab3_check.py). Lệnh [`eval/run_eval.py`](../eval/run_eval.py) chưa dùng được vì nó cần các hàm viết ở Lab 4 và Lab 5.

---

## Sáu khối code

| # | Hàm | Module | Chặng ở slide | Đặc tả |
|---|---|---|---|---|
| 1 | `chunk_document` | [`src/knowledge/preparation.py`](../src/knowledge/preparation.py) | Chunk | [SPEC-RAG-07](../PROJECT-SPEC.md#spec-rag-07) |
| 2 | `embed_chunks` | [`src/knowledge/embedding.py`](../src/knowledge/embedding.py) | Embed | [SPEC-RAG-08](../PROJECT-SPEC.md#spec-rag-08) |
| 3 | `hybrid_search` | [`src/retrieval/search.py`](../src/retrieval/search.py) | Retrieve | [SPEC-RAG-09](../PROJECT-SPEC.md#spec-rag-09) |
| 4 | `judge_evidence` | [`src/retrieval/filters.py`](../src/retrieval/filters.py) | Filter | [SPEC-RAG-10](../PROJECT-SPEC.md#spec-rag-10) |
| 5 | `assemble_context` | [`src/context/assemble.py`](../src/context/assemble.py) | Select, Assemble | [SPEC-CTX-01](../PROJECT-SPEC.md#spec-ctx-01) |
| 6 | `classify` | [`src/agent/classifier.py`](../src/agent/classifier.py) | Dùng Foundation Model | [SPEC-LLM-04](../PROJECT-SPEC.md#spec-llm-04) |

## Bước 1 — Instruction

Đọc `classify.v2.md`: ghép năm phần của [SPEC-PROMPT-01](../PROJECT-SPEC.md#spec-prompt-01) với slide 12, chỉ ra bốn hợp đồng ở slide 15, phân tích thẻ `<ticket>` (prompt injection, slide 13), xếp sáu mảnh của Mega Prompt (slide 18) vào đúng lớp.

Sản phẩm: bảng ghép, bảng bốn hợp đồng, phân tích.

## Bước 2 — Knowledge

Chạy `lab3_check.py ingest`. Ghép sáu bước vòng đời tri thức (slide 34) với hàm trong dự án, xếp thành phần vào bốn dạng tri thức (slide 30–31), điền sáu thuộc tính sẵn sàng (slide 33), và phân tích hậu quả nếu truy hồi không lọc `status` (hai cặp tài liệu mâu thuẫn).

Sản phẩm: các bảng phân loại, bảng hai cặp mâu thuẫn, phân tích.

## Bước 3 — Chia đoạn

Cài `chunk_document` (khối 1): chia theo mục, giữ siêu dữ liệu để trích dẫn. Xem kết quả bằng `lab3_check.py chunks` ở hai kích thước, và chọn tham số kèm lý do.

Sản phẩm: khối 1 qua `pytest -m lab3 -k chunk`, bảng tham số chia đoạn.

## Bước 4 — Embed và Index

Cài `embed_chunks` (khối 2): gọi model embedding theo lô. Chạy `lab3_check.py embed` để thấy vector và tìm theo nghĩa, rồi dựng chỉ mục bằng [`scripts/build_index.py`](../scripts/build_index.py).

Sản phẩm: khối 2 qua `pytest -m lab3 -k embed`, chỉ mục vector đã dựng.

## Bước 5 — Retrieval

1. Cài `hybrid_search` (khối 3) và `judge_evidence` (khối 4).
2. Đo baseline hai lượt bằng `lab3_check.py retrieval`: chỉ từ khóa và hybrid. So Recall@5, MRR, tỉ lệ từ chối đúng.
3. Chọn ngưỡng từ chối từ bảng quét ngưỡng, kiểm lại và ghi vào `.env` cùng `context_spec.md`.
4. Thử tối thiểu hai cải tiến, mỗi lần một biến: kích thước đoạn, bỏ tiêu đề, viết lại truy vấn, rerank, trọng số vector. Đo lại sau mỗi lần.
5. Chẩn đoán lỗi retrieval theo năm kiểu của slide 44.

Thử cải tiến mà không đo lại thì không được chấp nhận. Thay nhiều thứ cùng lúc cũng vậy, vì không quy được kết quả cho nguyên nhân nào.

Sản phẩm: khối 3, 4 qua `pytest -m lab3`, bảng baseline, bảng thí nghiệm, ngưỡng đã chọn.

## Bước 6 — Context và dùng model AI

1. Ghi hệ thống cung cấp sáu thành phần context (slide 20–21) bằng cách nào, thành phần nào chưa có.
2. Cài `assemble_context` (khối 5). Xem context thật bằng `lab3_check.py context` và lập bảng ngân sách (tổng dưới 3.000 token).
3. Cài `classify` (khối 6). Chạy `lab3_check.py layers` và `layers --live 20` để thấy bốn lớp phòng vệ đầu ra hoạt động.
4. Chạy `lab3_check.py ask` với một câu có đáp án và một câu không có đáp án: truy hồi, kiểm tra đủ căn cứ, ghép context, model trả lời có trích dẫn.

Sản phẩm: khối 5, 6 qua `pytest -m lab3`, bảng sáu thành phần, bảng ngân sách, bảng kết quả `ask`.

## Bước 7 — Viết Context Specification

Sao chép [`docs/context-spec-template.md`](../docs/context-spec-template.md) thành [`docs/context_spec.md`](../docs/context_spec.md) và điền chín mục từ workbook. Mỗi lựa chọn có lý do và số đo, mọi bảng số liệu ghi cấu hình S hoặc L. Đối chiếu với Blueprint ở Workbook 2 và ghi thay đổi thành ADR mới (từ `0011`).

---

## Nộp sau buổi học

- [`docs/context_spec.md`](../docs/context_spec.md) đầy đủ: instruction kèm lý do thiết kế, chia đoạn, embedding, ngưỡng từ chối chọn bằng số đo, bảng thí nghiệm, ngân sách context
- Mã 6 khối vượt `pytest -m lab3`
- Workbook 3 đã điền
- Pull request để một nhóm khác rà soát. Chuẩn bị sẵn checklist rà soát cho lượt của nhóm mình

## Tự kiểm tra

```bash
uv run pytest -m lab3
uv run python scripts/checkpoint.py 3
```

## Thang điểm (10)

| Tiêu chí | Điểm |
|---|---|
| Kho tri thức: chia đoạn đúng đặc tả, dựng được chỉ mục vector, hiểu vòng đời tài liệu (lọc `status`) | 2 |
| Retrieval hoạt động: keyword, semantic, hybrid; quy tắc không đủ căn cứ; ghép context có trích dẫn | 2 |
| Ngưỡng từ chối và các thí nghiệm có số đo: baseline hai lượt, quét ngưỡng, ≥ 2 thí nghiệm mỗi lần một biến | 2 |
| Dùng model AI: `classify` qua bốn lớp phòng vệ, `ask` cho câu trả lời có trích dẫn, phân tích lỗi retrieval | 2 |
| Tài liệu giải thích lý do lựa chọn, không chỉ mô tả đã làm gì | 2 |

## Lỗi thường gặp

| Tình huống | Cách xử lý |
|---|---|
| Cắt đoạn cứng theo số ký tự, đứt điều khoản | Chia theo mục, xem [SPEC-RAG-07](../PROJECT-SPEC.md#spec-rag-07) |
| `chunk_id` trùng vì đặt lại số thứ tự ở mỗi mục | Đánh số liên tục trong cả tài liệu |
| Chọn ngưỡng theo cảm giác | Chọn từ bảng quét ngưỡng và đo lại |
| Đổi model embedding, kiểu tìm hoặc kích thước đoạn mà giữ nguyên ngưỡng | Hiệu chuẩn lại ngưỡng |
| Thử cải tiến nhưng không đo lại | Chạy lại, mỗi lần một biến |
| Gọi model ở nơi khác ngoài `LLMClient` | Mọi lời gọi đi qua [`src/llm/client.py`](../src/llm/client.py) |
| `Không gọi được model` | Mở terminal khác, gõ `ollama serve`, kiểm tra `ollama list` có `bge-m3` |
| Máy chưa có `bge-m3` | Dùng `--search keyword` cho các bước đo, và báo giảng viên |

## Nếu xong sớm

Quản lý context theo thời gian (slide 26), cải tiến rerank, hoặc permission-aware retrieval (slide 44): xem cuối Workbook 3.
