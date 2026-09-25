# WORKBOOK 6 — Hoàn thiện và trình diễn

**Ngày 3, buổi chiều · 180 phút thực hành · Deliverable: Final AI Application**

| | |
|---|---|
| Nhóm | `______________` |
| Cấu hình báo cáo | S / L |
| Thứ tự trình diễn | `___/6` · giờ `___:___` |

---

## Bước 1 — Sprint cải tiến · 55 phút

**`___:___` → `___:___`**

### 1a. Hai cải tiến — chép từ cuối `WORKBOOK-5.md`

| # | Cải tiến | Dựa trên phát hiện nào ở Session 5 |
|---|---|---|
| 1 | `______________________________` | `______________________________` |
| 2 | `______________________________` | `______________________________` |

> Giới hạn **đúng hai** là có chủ ý: nó buộc xếp thứ tự ưu tiên bằng dữ liệu, và bảo đảm còn đủ thời gian đo lại. Nhóm làm năm cải tiến rồi không kịp đo cái nào sẽ không có gì để trình bày.

### 1b. Quy tắc — mỗi lần một biến

⚠︎ Đo lại **sau từng cải tiến**, không gộp. Thay nhiều thứ cùng lúc thì không quy được kết quả cho nguyên nhân nào.

```bash
uv run python eval/run_eval.py --background &
```

### Cải tiến 1

Đổi cụ thể cái gì: `_____________________________________________`

| Chỉ số | Trước | Sau | Chênh | **Cấu hình** |
|---|---|---|---|---|
| Accuracy | `______` | `______` | `______` | `S / L` |
| Macro-F1 | `______` | `______` | `______` | |
| Recall@5 | `______` | `______` | `______` | |
| Chuyển người đúng | `______` | `______` | `______` | |
| p95 | `______` | `______` | `______` | |

Có chỉ số nào **xấu đi** không? `___________________________________`

### Cải tiến 2

Đổi cụ thể cái gì: `_____________________________________________`

| Chỉ số | Trước | Sau | Chênh | **Cấu hình** |
|---|---|---|---|---|
| Accuracy | `______` | `______` | `______` | `S / L` |
| Macro-F1 | `______` | `______` | `______` | |
| Recall@5 | `______` | `______` | `______` | |
| Chuyển người đúng | `______` | `______` | `______` | |
| p95 | `______` | `______` | `______` | |

Có chỉ số nào **xấu đi** không? `___________________________________`

### 1c. Câu hỏi tự kiểm ⚠︎

Chênh lệch nhóm đo được có đủ lớn để tin không, với tập kiểm định chỉ 40 ticket?
`___________________________________________________________________`

MLflow run trước: `____________`  ·  run sau: `____________`

---

## Bước 2 — Model Card và gói bàn giao · 25 phút

**`___:___` → `___:___`**

### 2a. Kiểm tra thiên lệch

```bash
uv run python scripts/bias_check.py
```

| Chiều | Nhóm | Độ chính xác | Chuyển người | Số ca |
|---|---|---|---|---|
| Văn phong | ngắn gọn | `______` | `______` | `___` |
| | đầy đủ | `______` | `______` | `___` |
| Sắc thái | trung_tinh | `______` | `______` | `___` |
| | buc_boi | `______` | `______` | `___` |
| | gay_gat | `______` | `______` | `___` |
| Kênh | app | `______` | `______` | `___` |
| | hotline | `______` | `______` | `___` |
| | email | `______` | `______` | `___` |

**Chênh lệch lớn nhất: `______` ở chiều `____________`**  (ngưỡng cảnh báo 15 điểm %)

Vượt ngưỡng? `[ ] Không`  ·  `[ ] Có → phải ghi vào mục 2b như một giới hạn`

⚠︎ Nhóm nào dưới 5 ca thì **chưa đủ căn cứ kết luận**. Ghi rõ điều đó, đừng báo cáo như kết quả chắc chắn.

Nhóm nào trong bảng trên có dưới 5 ca? `_______________________________`

### 2b. Giới hạn đã biết ⚠︎ — tối thiểu ba, cụ thể

Viết chung chung kiểu *"hệ thống có thể sai trong một số trường hợp"* **không tính**.

**1.** `_________________________________________________________________`
`___________________________________________________________________`

**2.** `_________________________________________________________________`
`___________________________________________________________________`

**3.** `_________________________________________________________________`
`___________________________________________________________________`

Mỗi giới hạn rút ra từ phát hiện nào ở Session 5? Ghi rõ.

### 2c. Gói bàn giao

| Tệp | Xong? | Nội dung nhóm bổ sung riêng |
|---|---|---|
| [`docs/MODEL_CARD.md`](../docs/MODEL_CARD.md) | `[ ]` | `______________________` |
| `docs/handover/RUNBOOK.md` | `[ ]` | `______________________` |
| `docs/handover/INCIDENTS.md` | `[ ]` | `______________________` |
| `docs/handover/RESPONSIBILITIES.md` | `[ ]` | `______________________` |

**Câu hỏi tự kiểm:** đơn vị vận hành nhận sản phẩm này vào thứ Hai. Họ cần biết **ba** điều gì mà tài liệu của nhóm chưa nói?

`1. _______________________________________________________________`
`2. _______________________________________________________________`
`3. _______________________________________________________________`

Bổ sung ba điều đó vào `RESPONSIBILITIES.md` mục 5: `[ ]`

---

## Bước 3 — Chuẩn bị trình diễn · 30 phút

**`___:___` → `___:___`**

### 3a. Kịch bản 8 phút

| Phút | Nội dung | Ai nói |
|---|---|---|
| 0–1 | Bài toán và phạm vi | `________` |
| 1–2 | Kiến trúc 5 tầng | `________` |
| 2–6 | Bốn kịch bản demo | `________` |
| 6–7 | Kết quả đánh giá và hai cải tiến | `________` |
| 7–8 | Giới hạn đã biết và hướng phát triển | `________` |

### 3b. Bốn ticket demo — chuẩn bị sẵn mã, đã chạy thử

| # | Kịch bản | Mã ticket | Đã chạy thử? | Kết quả mong đợi |
|---|---|---|---|---|
| 1 | Xử lý trơn tru | `________` | `[ ]` | `______________` |
| 2 | Phải gọi công cụ | `________` | `[ ]` | `______________` |
| 3 | Bị chuyển người | `________` | `[ ]` | `______________` |
| 4 | **Đối kháng bị chặn** | `________` | `[ ]` | `______________` |

### 3c. Video dự phòng ⚠︎ bắt buộc

`[ ]` Đã quay toàn bộ demo  ·  Tệp: `____________________`

> Khi cả lớp cùng chạy model vào giờ trình diễn, tốc độ có thể chậm bất thường. Yêu cầu này không phải hình thức.

---

## Bước 4 — Trình bày và phản biện · 60 phút

**`___:___` → `___:___`**

### 4a. Chuẩn bị trả lời — điền TRƯỚC khi lên trình bày

| Câu hỏi | Câu trả lời của nhóm |
|---|---|
| Vì sao chọn kích thước đoạn như vậy? Đã thử gì khác, kết quả ra sao? | `________________________` |
| Ngưỡng chuyển người dựa trên căn cứ gì? Hạ ngưỡng thì đánh đổi là gì? | `________________________` |
| Lưu lượng tăng gấp mười thì nút thắt ở đâu? | `________________________` |
| Hệ thống phục vụ bao nhiêu ticket/giờ? Đủ cho giả định trong Canvas không? | `________________________` |
| Hệ thống có xử lý khác nhau giữa các nhóm khách hàng không? Kiểm chứng thế nào? | `________________________` |
| Đơn vị vận hành cần biết gì mà tài liệu chưa nói? | `________________________` |
| Hệ thống trả lời sai một khách hàng — truy vết thế nào, mất bao lâu? | `________________________` |
| Trường hợp nào hệ thống gây rủi ro nghiệp vụ? Đã có biện pháp gì? | `________________________` |
| Con số báo cáo đo trên tập nào, cấu hình nào? Chạy lại có ra tương tự? | `________________________` |
| Phải lên môi trường thật tuần sau — ba việc làm trước tiên? | `________________________` |
| Đâu là điều hệ thống chắc chắn **không** làm được? Biết bằng cách nào? | `________________________` |

> Nguồn trả lời cho ba câu đầu nằm ở **bảng quyết định thiết kế** trong `WORKBOOK-2.md` và các ADR. Đó là lý do bảng đó phải ghi nghiêm túc từ ngày 1.

### 4b. Trình bày quyết định, không trình bày tính năng

Chọn **một** quyết định thiết kế để trình bày kỹ:

| Phần | Nội dung |
|---|---|
| Bối cảnh | `___________________________________________` |
| Các phương án đã cân nhắc | `___________________________________________` |
| Tiêu chí lựa chọn | `___________________________________________` |
| Hệ quả chấp nhận | `___________________________________________` |

### 4c. Ghi nhận phản biện

| Nhóm hỏi | Câu hỏi | Trả lời được? | Nếu không — vì sao |
|---|---|---|---|
| `______` | `________________________` | `[ ]` | `______________` |
| `______` | `________________________` | `[ ]` | `______________` |
| `______` | `________________________` | `[ ]` | `______________` |

### 4d. Nhóm mình hỏi nhóm khác

| Hỏi nhóm | Câu hỏi | Điều học được từ câu trả lời |
|---|---|---|
| `______` | `________________________` | `______________________` |

---

## Bước 5 — Tổng kết · 10 phút

**`___:___` → `___:___`**

### Nhóm khác làm khác mình ở đâu

| Quyết định | Nhóm mình | Nhóm khác | Cả hai cùng đúng được không? Vì sao |
|---|---|---|---|
| Ngưỡng truy hồi | `______` | `______` | `______________________` |
| Ngưỡng chuyển người | `______` | `______` | `______________________` |
| Chiến lược chia đoạn | `______` | `______` | `______________________` |

### Ba điều rút ra sau toàn khóa

`1. _______________________________________________________________`
`2. _______________________________________________________________`
`3. _______________________________________________________________`

### Về việc dùng trợ lý lập trình AI · 10 phút thảo luận

Nhóm có dùng trợ lý AI không? `[ ] Có`  ·  `[ ] Không`

**Điều gì thay đổi trong khâu rà soát mã và kiểm thử khi phần lớn mã do AI sinh ra?**
`___________________________________________________________________`
`___________________________________________________________________`

Cổng chất lượng tự động trở nên **quan trọng hơn** hay **kém đi**? Vì sao?
`___________________________________________________________________`

Có dòng mã nào trong bài nộp mà nhóm **không giải thích được** không? `[ ] Không`  ·  `[ ] Có ⚠︎`

---

## Nộp cuối khóa

- [ ] Hệ thống hoàn chỉnh trên nhánh nhóm, PR đã được nhóm khác duyệt
- [ ] Slide ~10 trang
- [ ] Gói bàn giao: README dựng lại · sổ tay vận hành · quy trình xử lý sự cố
- [ ] Model Card kèm kết quả kiểm tra thiên lệch
- [ ] Bảng so sánh trước–sau của hai cải tiến
- [ ] Toàn bộ 6 workbook đã điền, commit vào [`docs/workbook/`](../docs/workbook/)

```bash
uv run pytest
uv run python scripts/checkpoint.py 6 --team ______
git tag submit/final-______ && git push --tags
```
