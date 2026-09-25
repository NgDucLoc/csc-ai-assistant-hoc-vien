# WORKBOOK 4 — Xây dựng quy trình xử lý AI

**Ngày 2, buổi chiều · 120 phút thực hành · Deliverable: AI Prototype v1**

| | |
|---|---|
| Nhóm | `______________` |
| Cấu hình | S / L |

> ⚠︎ **Buổi dễ vỡ nhất toàn khóa.** Nó dựa thẳng lên phần RAG làm sáng nay và **không có đêm để bù**.
>
> Nếu `checkpoint.py 3` chưa PASS, chạy `./scripts/rescue.sh 3` **ngay bây giờ**, trước khi bắt đầu. Đừng cố làm bù.

Nhóm đã chạy cứu hộ chưa? `[ ] Không cần`  ·  `[ ] Đã chạy`

---

## Sáu khối phải hoàn thành

| # | Hàm | Tệp | Xong? |
|---|---|---|---|
| 1 | `validate_args` | [`src/agent/tools.py`](../src/agent/tools.py) | `[ ]` |
| 2 | `rule_based_plan` | [`src/agent/tools.py`](../src/agent/tools.py) | `[ ]` |
| 3 | `check_input` | [`src/guardrails/input_rules.py`](../src/guardrails/input_rules.py) | `[ ]` |
| 4 | `generate_reply` | [`src/agent/generator.py`](../src/agent/generator.py) | `[ ]` |
| 5 | `process_ticket` | [`src/agent/workflow.py`](../src/agent/workflow.py) | `[ ]` |
| 6 | `Store.record_review` | [`src/store.py`](../src/store.py) | `[ ]` |

---

## Bước 0 — Rà soát chéo · 10 phút

**`___:___` → `___:___`**

Đổi pull request với nhóm `______`.

| Kiểm | Kết quả |
|---|---|
| Prompt đủ 5 phần và có thẻ `<ticket>` phân tách? | `[ ]` |
| Bốn lớp phòng vệ đủ? Lớp 3 có đưa lỗi vào prompt? | `[ ]` |
| Truy hồi có lọc `status: superseded`? | `[ ]` |
| Bảng số liệu có cột **cấu hình**? | `[ ]` |
| Có lời gọi model nào ngoài [`src/llm/client.py`](../src/llm/client.py)? | `[ ]` không có |

Nhận xét gửi nhóm bạn: `______________________________________________`

Nhận xét nhóm bạn gửi mình: `_________________________________________`

> Bấm approve cho xong là bỏ mất giá trị của bước này.

---

## Bước 1 — Thiết kế quy trình TRÊN GIẤY · 30 phút

**`___:___` → `___:___`**

⚠︎ Vẽ xong mới viết code. Nhóm nào viết code trước sẽ chỉ ghép được luồng thuận lợi.

### 1a. Sơ đồ luồng có nhánh rẽ

Vẽ tay, chụp ảnh đính kèm: `____________________`

Liệt kê các **điểm quyết định** trong sơ đồ:

| # | Ở bước nào | Điều kiện rẽ | Rẽ đi đâu |
|---|---|---|---|
| 1 | `____________` | `______________` | `____________` |
| 2 | `____________` | `______________` | `____________` |
| 3 | `____________` | `______________` | `____________` |
| 4 | `____________` | `______________` | `____________` |

### 1b. Điều kiện chuyển người ⚠︎ — tối thiểu bốn, mỗi điều kiện kèm lý do

| # | Điều kiện | Ngưỡng cụ thể | **Vì sao phải chuyển người** |
|---|---|---|---|
| 1 | `________________` | `________` | `______________________________` |
| 2 | `________________` | `________` | `______________________________` |
| 3 | `________________` | `________` | `______________________________` |
| 4 | `________________` | `________` | `______________________________` |
| 5 | `________________` | `________` | `______________________________` |

Gợi ý nếu bí: độ tin cậy thấp · không đủ căn cứ · khách đòi bồi thường tiền · ticket P1 · khách dọa khiếu nại lên cấp trên.

**Ngưỡng độ tin cậy nhóm chọn: `______`**  Vì sao con số đó mà không phải cao hơn hay thấp hơn?
`___________________________________________________________________`

> Câu này sẽ bị hỏi ở phần phản biện Session 6: *"Hạ ngưỡng xuống thì đánh đổi là gì?"* Trả lời trước đi:
> `_______________________________________________________________`

---

## Bước 2 — Công cụ và đường dự phòng · 30 phút

**`___:___` → `___:___`**

### 2a. Ba công cụ

| Công cụ | Tham số | Trả về | Đã chạy được? |
|---|---|---|---|
| `get_subscriber_info` | `______________` | `______________` | `[ ]` |
| `get_billing_history` | `______________` | `______________` | `[ ]` |
| `check_area_incident` | `______________` | `______________` | `[ ]` |

Ràng buộc bắt buộc: `[ ]` chỉ đọc · `[ ]` timeout 5s · `[ ]` tối đa 3 lần/ticket · `[ ]` validate tham số trước khi chạy

### 2b. Model gọi công cụ sai như thế nào ⚠︎

Cho model tự chọn công cụ trên 10 ticket. Ghi lại **các kiểu gọi sai thực sự gặp**:

| Kiểu sai | Số ca | Ví dụ cụ thể |
|---|---|---|
| Không gọi công cụ nào | `___/10` | |
| Sai tên công cụ | `___/10` | `______________________` |
| Sai kiểu tham số | `___/10` | `______________________` |
| Thiếu tham số bắt buộc | `___/10` | `______________________` |

**Tỉ lệ gọi công cụ đúng: `____%`** — ghi lại, Session 5 sẽ dùng con số này để phân tích.

### 2c. Đường dự phòng theo luật

| Điều kiện | Công cụ gọi tự động |
|---|---|
| `category = cuoc_thanh_toan` + có `subscriber_id` | `______________________` |
| `category = chat_luong_ket_noi` + có `subscriber_id` | `______________________` |
| Mọi ticket có `subscriber_id` hợp lệ | `______________________` |

> Việc phải xây đường dự phòng cho quyết định của model là **một nguyên tắc thiết kế**, không phải một sự thỏa hiệp kỹ thuật.
>
> Nhóm còn thấy chỗ nào khác trong hệ thống mà quyết định của model cũng cần đường lùi tất định?
> `_______________________________________________________________`

---

## Bước 3 — Sinh phản hồi và ghép quy trình · 35 phút

**`___:___` → `___:___`**

### 3a. Sáu ràng buộc trong prompt sinh phản hồi

Đánh dấu ràng buộc nào nhóm đã đưa vào `generate.v1.md`:

`[ ]` chỉ dùng thông tin trong ngữ cảnh
`[ ]` mỗi khẳng định kèm trích dẫn `[KB-xxx vN, hiệu lực YYYY-MM-DD]`
`[ ]` **không cam kết bồi thường hay số tiền cụ thể**
`[ ]` không hứa mốc thời gian
`[ ]` không nhắc PII, không nhắc thuê bao khác
`[ ]` không đủ căn cứ → trả `KHÔNG ĐỦ CĂN CỨ`

### 3b. Chạy thử 5 ticket đa dạng ⚠︎ — phải có một ticket rác

| # | Mã ticket | Loại | Trạng thái cuối | Lý do chuyển người (nếu có) |
|---|---|---|---|---|
| 1 | `________` | trơn tru | `______________` | |
| 2 | `________` | gọi công cụ | `______________` | `______________` |
| 3 | `________` | không đủ căn cứ | `______________` | `______________` |
| 4 | `________` | tranh chấp tiền | `______________` | `______________` |
| 5 | `________` | **rác** | `______________` | `______________` |

**Ticket rác:** hệ thống có văng lỗi không? `[ ] Không — chuyển người có kiểm soát`  `[ ] Có ⚠︎ phải sửa`

Số lời gọi model cho ticket rác: `______` (kỳ vọng **0**)

---

## Bước 4 — Màn hình duyệt và nhật ký · 25 phút

**`___:___` → `___:___`**

### 4a. Thứ tự thông tin trên màn hình ⚠︎

Đánh số thứ tự nhóm đã cài đặt: `___` ticket gốc · `___` phân loại · `___` đoạn tri thức · `___` dự thảo

**Vì sao dự thảo KHÔNG được đặt lên đầu?**
`___________________________________________________________________`

### 4b. Ba lựa chọn của người duyệt

`[ ]` Duyệt   `[ ]` Sửa rồi duyệt   `[ ]` Từ chối **kèm lý do bắt buộc**

Thử từ chối mà bỏ trống lý do — hệ thống làm gì? `_______________________`

### 4c. Nhật ký thao tác

Thực hiện 4 thao tác duyệt rồi mở trang Theo dõi:

| Chỉ số | Giá trị |
|---|---|
| Tỉ lệ duyệt thẳng | `____%` |
| Tỉ lệ phải sửa | `____%` |
| Tỉ lệ từ chối | `____%` |

> Nhật ký thao tác duyệt **không phải để giao diện trông đầy đủ**. Tỉ lệ sửa và lý do từ chối là chỉ số chất lượng đáng tin cậy nhất mà hệ thống có, và là nguồn dữ liệu chính cho sprint cải tiến ở Session 6.

**Nếu thiếu thời gian:** ưu tiên phần ghi nhật ký, giao diện có thể đơn giản hóa.

---

## Mốc kiểm tra cuối buổi · 5 phút

```bash
uv run pytest -m lab4
uv run python scripts/checkpoint.py 4 --team ______
```

Kết quả: `[ ] ĐỦ ĐIỀU KIỆN`  ·  `[ ] THIẾU ____/____`

Bài kiểm thử quan trọng nhất: `test_no_path_reaches_customer_without_human_approval` → `[ ] xanh`

### Nộp
- [ ] Prototype chạy thông từ ticket tới dự thảo chờ duyệt
- [ ] **Video ~2 phút**, ba tình huống: trơn tru · gọi công cụ · chuyển người
- [ ] Sơ đồ luồng cập nhật, phản ánh đúng cái đã cài đặt

---

## Nếu xong sớm

Vòng lặp agent thực thụ cho nhánh phức tạp, **có giới hạn số vòng**.

| | Quy trình cố định | Agent |
|---|---|---|
| Độ chính xác | `______` | `______` |
| Lời gọi model TB | `______` | `______` |
| p95 độ trễ | `______` | `______` |

**Agent có đáng không, và với loại ticket nào?** `_________________________`
