# CONTEXT SPECIFICATION — <Tên nhóm>

> **Cách dùng khung này:** sao chép thành [`docs/context_spec.md`](../docs/context_spec.md) rồi điền. Lệnh: `cp docs/context-spec-template.md docs/context_spec.md` (Windows: `copy docs\context-spec-template.md docs\context_spec.md`). Xóa các dòng "Gợi ý:" sau khi điền xong.
>
> Một tài liệu chỉ nêu "chúng tôi dùng chunk 700 ký tự" mà không nói vì sao thì chưa đạt. Mỗi lựa chọn cần lý do, và mỗi con số cần số đo đi kèm cùng cấu hình (S hoặc L) sinh ra nó.

| | |
|---|---|
| Nhóm | |
| Ngày | |
| Cấu hình đo | S / L |
| Model sinh văn bản / model embedding | |
| ADR liên quan | `docs/adr/0011` … |

---

## 1. Thiết kế instruction

Gợi ý: lấy từ Bước 1 của Workbook 3.

Nêu các prompt trong [`src/agent/prompts/`](../src/agent/prompts/), cách chúng khớp năm phần của [SPEC-PROMPT-01](../PROJECT-SPEC.md#spec-prompt-01) và bốn hợp đồng của slide 15. Nội dung ticket được đặt ở đâu trong prompt, và lớp phòng vệ nào bổ sung cho thẻ `<ticket>`? Vì sao phân loại và soạn phản hồi ở hai lời gọi riêng?

| Tệp | Phiên bản | Việc | Ghi chú |
|---|---|---|---|
| `classify.v1.md` | 1 | | |
| `classify.v2.md` | 2 | | |
| `generate.v1.md` | 1 | | |
| `rewrite_query.v1.md` | 1 | | |

## 2. Knowledge và vòng đời tài liệu

Gợi ý: lấy từ Bước 2. Nêu các dạng tri thức của hệ thống, thuộc tính nào trong sáu thuộc tính của slide 33 đã đáp ứng, còn thiếu gì, và cách xử lý hai cặp tài liệu mâu thuẫn.

| Thuộc tính | Cơ chế đáp ứng | Còn thiếu |
|---|---|---|
| Findable | | |
| Understandable | | |
| Authoritative | | |
| Fresh | | |
| Traceable | | |
| Governed | | |

## 3. Chia đoạn

Gợi ý: lấy từ Bước 3.

| Tham số | Giá trị | Vì sao |
|---|---|---|
| Cách chia | | |
| Kích thước tối đa | | |
| Chồng lấn | | |
| Gắn tiêu đề tài liệu và mục | | |
| Lọc theo `status` | | |

## 4. Embedding và chỉ mục

Gợi ý: lấy từ Bước 4. Nêu model embedding, số chiều vector, cách dựng chỉ mục, vì sao model embedding phải giống nhau ở cả hai cấu hình, và khi nào phải dựng lại chỉ mục.

## 5. Retrieval và quy tắc từ chối

Gợi ý: lấy từ Bước 5c.

| Tham số | Giá trị | Vì sao |
|---|---|---|
| Kiểu tìm | keyword / semantic / hybrid | |
| Trọng số vector | | |
| `top_k` | | |
| Ngưỡng `RETRIEVE_MIN_SCORE` | | |

| Chỉ số | Chỉ từ khóa | Hybrid | Cấu hình đo |
|---|---|---|---|
| Recall@5 | | | |
| MRR | | | |
| Tỉ lệ từ chối đúng | | | |
| Từ chối thừa | | | |

Bảng quét ngưỡng của nhóm và cách chọn ngưỡng (đánh đổi giữa bịa và từ chối thừa). Liên hệ [ADR-0005](../docs/adr/0005-nguong-tu-choi-thay-vi-doan.md).

## 6. Thí nghiệm cải tiến retrieval

Gợi ý: tối thiểu hai thí nghiệm, mỗi lần đổi một biến, có cột cấu hình. Ghi thí nghiệm nào buộc phải hiệu chuẩn lại ngưỡng.

| # | Đổi gì | Recall@5 trước | Recall@5 sau | Từ chối đúng trước | Từ chối đúng sau | Cấu hình |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |

Chẩn đoán lỗi theo năm kiểu của slide 44 (Missed Evidence, Irrelevant Retrieval, Stale Retrieval, Conflicting Evidence, Unauthorized Retrieval): kiểu nào nhóm đã gặp, kiểu nào cơ chế hiện có còn yếu.

## 7. Context và ngân sách

Gợi ý: lấy từ Bước 6a và 6b. Trần 3.000 token mỗi lời gọi ([SPEC-INFRA-04](../PROJECT-SPEC.md#spec-infra-04)).

| Thành phần context | Hệ thống cung cấp bằng | Ghi chú |
|---|---|---|
| Subscriber State | | |
| Enterprise Knowledge | | |
| Conversation / Task State | | |
| System State | | |
| Tool Results | | |
| Permissions / Constraints | | |

| Thành phần | Ngân sách | Đo được |
|---|---|---|
| Prompt hệ thống | | |
| Nội dung ticket | | |
| Đoạn tri thức (khối context) | | |
| Kết quả gọi công cụ | | |
| Chừa cho đầu ra | | |
| Tổng | | |

Vì sao ngân sách được ép bằng kiểm thử tự động thay vì để tốc độ của máy tự ép?

## 8. Đầu ra có cấu trúc và bốn lớp phòng vệ

Gợi ý: lấy từ Bước 6c.

| Lớp | Cơ chế | Kiểu hỏng bắt được | Ví dụ nhóm gặp |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

| Chỉ số | Chỉ lớp 1 | Thêm lớp 2 | Đủ 4 lớp | Cấu hình đo |
|---|---|---|---|---|
| Tỉ lệ phân tích cú pháp thành công | | | | |
| Tỉ lệ phải dùng lớp dự phòng | | | | |
| Số lần gọi model trung bình mỗi ticket | | | | |

## 9. Điều chưa giải quyết

Gợi ý: ít nhất hai giới hạn thật, cùng những chỗ đo chưa đạt ngưỡng của [SPEC-SCOPE-03](../PROJECT-SPEC.md#spec-scope-03).

-
-
