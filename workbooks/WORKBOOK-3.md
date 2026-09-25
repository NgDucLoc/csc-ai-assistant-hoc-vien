# WORKBOOK 3 — Xây dựng trí tuệ cho ứng dụng AI

**Ngày 2, buổi sáng · 120 phút thực hành · Deliverable: [`docs/context_spec.md`](../docs/context_spec.md)**

| | |
|---|---|
| Nhóm | `______________` |
| Cấu hình đang dùng | S / L |
| Model | `______________` |

> **Buổi đầu tiên viết code thật: 6 khối `LAB-3`.**
>
> ⚠︎ Session 4 chiều nay dựa **thẳng** lên phần RAG làm sáng nay, và giữa hai buổi chỉ có giờ nghỉ trưa. Chạy `checkpoint.py 3` trong 5 phút cuối buổi — đừng để tới đầu giờ chiều mới biết mình chưa xong.

---

## Sáu khối phải hoàn thành

| # | Hàm | Tệp | Xong? |
|---|---|---|---|
| 1 | `extract_json` | [`src/llm/schema.py`](../src/llm/schema.py) | `[ ]` |
| 2 | `validate` | [`src/llm/schema.py`](../src/llm/schema.py) | `[ ]` |
| 3 | `parse_with_retry` | [`src/llm/schema.py`](../src/llm/schema.py) | `[ ]` |
| 4 | `chunk_document` | [`src/knowledge/indexer.py`](../src/knowledge/indexer.py) | `[ ]` |
| 5 | `Retriever.retrieve` | [`src/knowledge/retriever.py`](../src/knowledge/retriever.py) | `[ ]` |
| 6 | `classify` | [`src/agent/classifier.py`](../src/agent/classifier.py) | `[ ]` |

Xem còn khối nào chưa làm:
```bash
grep -rn 'NotImplementedError("LAB-3' --include='*.py' src/
```

---

## Bước 1 — Prompt và ngân sách ngữ cảnh · 30 phút

**`___:___` → `___:___`**

### 1a. Cấu trúc năm phần

Mở [`src/agent/prompts/classify.v2.md`](../src/agent/prompts/classify.v2.md). Đánh dấu phần nào có:

`[ ] VAI TRÒ`  `[ ] NHIỆM VỤ`  `[ ] RÀNG BUỘC`  `[ ] NGỮ CẢNH`  `[ ] ĐỊNH DẠNG ĐẦU RA`

Nhóm sửa gì trong prompt so với bản v2 có sẵn? Vì sao?
`___________________________________________________________________`
`___________________________________________________________________`

### 1b. Bảng ngân sách ngữ cảnh

| Thành phần | Ngân sách nhóm đặt | Đo được thực tế |
|---|---|---|
| Prompt hệ thống | `______ token` | `______ token` |
| Nội dung ticket | `______ token` | `______ token` |
| Đoạn tri thức truy hồi | `______ token` | `______ token` |
| Kết quả gọi công cụ | `______ token` | `______ token` |
| Chừa cho đầu ra | `______ token` | — |
| **Tổng** | `______` | `______` |

Trần cứng: **3000 token** ([`SPEC-INFRA-04`](../PROJECT-SPEC.md#spec-infra-04)), ép bằng `pytest`.

> **Vì sao ép bằng kiểm thử chứ không để tốc độ phần cứng tự ép?**
> `_______________________________________________________________`

### 1c. Chạy thử 20 ticket, TRƯỚC khi làm lớp phòng vệ

```bash
uv run python eval/run_eval.py --set train --limit 20 --skip-adversarial
```

| Chỉ số | Giá trị | **Cấu hình** |
|---|---|---|
| Tỉ lệ phân tích cú pháp thành công | `____%` | `S / L` |
| Số ca model trả sai định dạng | `___/20` | |

Chép lại **một đầu ra sai định dạng** mà nhóm gặp:
```
_________________________________________________________________
```

---

## Bước 2 — Bốn lớp phòng vệ · 30 phút

**`___:___` → `___:___`**

| Lớp | Cơ chế | Bắt được kiểu hỏng nào nhóm thực sự gặp |
|---|---|---|
| 1 · lược đồ | `validate()` | `_______________________________` |
| 2 · bóc tách | `extract_json()` | `_______________________________` |
| 3 · thử lại | đưa lỗi vào prompt | `_______________________________` |
| 4 · dự phòng | `needs_human` | `_______________________________` |

### Bảng trước–sau ⚠︎ — đây là kết quả chính phải nộp

```bash
uv run pytest -m lab3 -k layer      # kiểm chứng bốn lớp
uv run python eval/run_eval.py --set train --limit 20 --skip-adversarial
```

| Chỉ số | Chỉ lớp 1 | Đủ 4 lớp | **Cấu hình** |
|---|---|---|---|
| Tỉ lệ phân tích cú pháp thành công | `____%` | `____%` | `S / L` |
| Tỉ lệ phải dùng lớp dự phòng | — | `____%` | |
| Số lời gọi model TB / ticket | `____` | `____` | |

### Bài học cần chốt ⚠︎

> Một ứng dụng AI đáng tin không phải nhờ model giỏi, mà nhờ tầng xử lý bao quanh model.

Con số nào trong bảng trên là bằng chứng cho câu đó?
`___________________________________________________________________`

**Điểm mấu chốt của lớp 3:** bảo model *"sai định dạng, làm lại"* khác gì so với gọi lại y hệt?
`___________________________________________________________________`

---

## Bước 3 — Kho tri thức · 35 phút

**`___:___` → `___:___`**

### 3a. Chiến lược chia đoạn

| Tham số | Nhóm chọn | Vì sao |
|---|---|---|
| Cách chia | theo mục / theo ký tự | `______________________` |
| Kích thước tối đa | `______ ký tự` | `______________________` |
| Chồng lấn | `______ ký tự` | `______________________` |
| Gắn tiêu đề vào đầu đoạn | Có / Không | `______________________` |

### 3b. Bẫy tài liệu mâu thuẫn ⚠︎

```bash
uv run python -c "from src.knowledge.loader import conflict_report; print(conflict_report())"
```

| Tài liệu cũ | Tài liệu mới | Nội dung mâu thuẫn ở đâu |
|---|---|---|
| `KB-____` | `KB-____` | `_________________________________` |
| `KB-____` | `KB-____` | `_________________________________` |

**Chuyện gì xảy ra nếu truy hồi KHÔNG lọc theo `status`?** Nêu một hậu quả cụ thể với khách hàng:
`___________________________________________________________________`

### 3c. Dựng chỉ mục

```bash
uv run python scripts/build_index.py
```

Số đoạn: `______` · Thời gian: `______` · Model nhúng: `______`

`[ ]` Nhóm tự dựng được  ·  `[ ]` Dùng bản dựng sẵn [`data/index_prebuilt/`](../data/index_prebuilt/)

> Dùng bản dựng sẵn **không mất điểm**. Ngồi chờ 4 phút mới mất điểm.

---

## Bước 4 — Đo và cải tiến truy hồi · 25 phút

**`___:___` → `___:___`**

### 4a. Đo đường nền

```bash
uv run python eval/run_eval.py --skip-adversarial --limit 20
```

| Chỉ số | Giá trị | Ngưỡng đạt | **Cấu hình** |
|---|---|---|---|
| Recall@5 | `______` | 0.78 (S) / 0.75 (L) | `S / L` |
| MRR | `______` | — | |
| **Tỉ lệ từ chối đúng** | `______` | mong muốn 1.0 | |

⚠︎ Chú ý dòng cuối: đó là tỉ lệ hệ thống nói *"không đủ căn cứ"* đúng trên **5 câu hỏi không có đáp án trong kho**. Chỉ số này quan trọng ngang Recall.

Nếu tỉ lệ đó < 1.0, hệ thống đang **bịa** ở câu nào?
`___________________________________________________________________`

### 4b. Hai thí nghiệm cải tiến ⚠︎ — mỗi lần một biến

| # | Đổi gì | Từ | Sang | Recall@5 trước | Recall@5 sau | **Cấu hình** |
|---|---|---|---|---|---|---|
| 1 | `____________` | `____` | `____` | `______` | `______` | `S / L` |
| 2 | `____________` | `____` | `____` | `______` | `______` | `S / L` |

Cải tiến nào hiệu quả hơn, và nhóm giải thích vì sao?
`___________________________________________________________________`

> Thử cải tiến mà **không đo lại** là không chấp nhận được. Thay nhiều thứ cùng lúc cũng vậy — sẽ không quy được kết quả cho nguyên nhân nào.

### 4c. So sánh hai phiên bản prompt

```bash
npx promptfoo@latest eval -c promptfooconfig.yaml && npx promptfoo@latest view
```

| Ca kiểm thử | v1 | v2 | Nhận xét |
|---|---|---|---|
| Cước cao bất thường | `___` | `___` | |
| Mất sóng diện rộng | `___` | `___` | |
| RANH GIỚI — nhắc gói nhưng đã mất tiền | `___` | `___` | |
| RANH GIỚI — hỏi điều khoản, chưa mất tiền | `___` | `___` | |
| **MƠ HỒ — độ tin cậy phải < 0.6** | `___` | `___` | |
| ĐỐI KHÁNG — chèn lệnh | `___` | `___` | |

Ca **MƠ HỒ** là chỗ v2 khác v1 rõ nhất. v1 trả độ tin cậy bao nhiêu? `______`  v2? `______`

Vì sao khác biệt đó quan trọng với hệ thống?
`___________________________________________________________________`

---

## Mốc kiểm tra cuối buổi · 5 phút ⚠︎ BẮT BUỘC

```bash
uv run pytest -m lab3
uv run python scripts/checkpoint.py 3 --team ______
```

Kết quả: `[ ] ĐỦ ĐIỀU KIỆN`  ·  `[ ] THIẾU ____/____`

**Nếu THIẾU — làm ngay bây giờ, không để tới chiều:**
```bash
./scripts/rescue.sh 3
```
Lệnh này **không đụng vào [`docs/`](../docs/)** — canvas, blueprint và ADR của nhóm giữ nguyên.

Nhóm có dùng cứu hộ không? `[ ] Không`  ·  `[ ] Có — đã đọc bản khác biệt: [ ]`

### Nộp
- [ ] [`docs/context_spec.md`](../docs/context_spec.md) đầy đủ, **có giải thích lý do lựa chọn**, không chỉ mô tả đã làm gì
- [ ] `uv run pytest -m lab3` xanh
- [ ] Pull request, chờ nhóm khác rà soát **đầu Session 4** (không qua đêm — không có đêm)

---

## Nếu xong sớm

Tìm kiếm lai: quét trọng số vector/từ khóa và đo Recall@5 tại mỗi mức.

| Trọng số vector | 0.0 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---|---|---|---|---|
| Recall@5 | `____` | `____` | `____` | `____` | `____` |

Trọng số tối ưu: `______`. Nó có ổn định giữa các nhóm câu hỏi không? `______`
