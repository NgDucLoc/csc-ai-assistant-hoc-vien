# WORKBOOK 5 — Tích hợp, triển khai và đánh giá

**Ngày 3, buổi sáng · 120 phút thực hành · Deliverable: [`docs/EVALUATION.md`](../docs/EVALUATION.md) + hệ thống đóng gói**

| | |
|---|---|
| Nhóm | `______________` |
| Cấu hình chuẩn của lớp | S / L |
| **Khe giờ đo tải trên server** | `___:___ → ___:___` |

---

## ⚠︎ HAI VIỆC LÀM NGAY PHÚT ĐẦU

Không làm ngay là vỡ giờ. Đọc trước khi ngồi vào máy.

### 1. Khởi động đánh giá chạy nền

```bash
uv run python eval/run_eval.py --background &
watch -n5 cat eval/results/progress.json
```

Giờ khởi động: `___:___`   ·   Xong lúc: `___:___`

Đánh giá 40 ticket trên CPU lâu hơn 30 phút của bước 2. Làm bước 1 trong lúc chờ.

### 2. Ghi khe giờ đo tải server vào ô trên cùng

`bench_server.py` **tự từ chối** chạy sai khe. Đó là chủ ý, không phải lỗi — sáu nhóm cùng đo trên một server sẽ làm số liệu của nhau nhiễu tới mức không dùng được.

---

## Năm khối phải hoàn thành

| # | Hàm | Tệp | Xong? |
|---|---|---|---|
| 1 | `check_output` | [`src/guardrails/output_rules.py`](../src/guardrails/output_rules.py) | `[ ]` |
| 2 | `TraceLogger.step` | [`src/guardrails/runtime.py`](../src/guardrails/runtime.py) | `[ ]` |
| 3 | `classification_metrics` | [`eval/metrics.py`](../eval/metrics.py) | `[ ]` |
| 4 | `retrieval_metrics` | [`eval/metrics.py`](../eval/metrics.py) | `[ ]` |
| 5 | `safety_metrics` | [`eval/metrics.py`](../eval/metrics.py) | `[ ]` |

---

## Bước 1 — API bất đồng bộ và đóng gói · 30 phút

**`___:___` → `___:___`**

### 1a. Vì sao bất đồng bộ ⚠︎

Mỗi ticket mất bao lâu ở cấu hình của nhóm? `______ giây`

Nếu API đồng bộ, client phải chờ bao lâu? `______ giây`

**Vì sao mô hình đồng bộ không hợp lệ với độ trễ đó?**
`___________________________________________________________________`

### 1b. Bảng điểm cuối

| Điểm cuối | Trả về gì | Đã chạy? |
|---|---|---|
| `POST /tickets` | `______________` | `[ ]` |
| `GET /jobs/{id}` | `______________` | `[ ]` |
| `GET /review/queue` | `______________` | `[ ]` |
| `POST /review/{id}` | `______________` | `[ ]` |
| `GET /trace/{id}` | `______________` | `[ ]` |
| `GET /health` · `/metrics` | `______________` | `[ ]` |

Tài liệu API tự sinh tại `http://localhost:8000/docs`: `[ ]` đã kiểm

### 1c. Đóng gói

```bash
docker compose up --build
```

`[ ]` Ba dịch vụ lên  ·  `[ ]` Docker lỗi → chạy trực tiếp (vẫn được chấm qua tệp cấu hình)

**Vì sao dịch vụ model đặt NGOÀI container?** (đọc [ADR-0004](../docs/adr/0004-dich-vu-model-ngoai-container.md))
`___________________________________________________________________`

---

## Bước 2 — Đọc kết quả và phân tích lỗi · 30 phút

**`___:___` → `___:___`**

Kết quả từ lệnh chạy nền lúc đầu buổi giờ đã có. **Đây là thời gian phân tích, không phải thời gian chờ.**

### 2a. Năm nhóm chỉ số ⚠︎ mọi dòng ghi cấu hình

**Cấu hình đo: `S / L`  ·  Model: `______________`  ·  Tập: `gold_test` 40 ticket**

| Nhóm | Chỉ số | Đo được | Ngưỡng đạt | Kết luận |
|---|---|---|---|---|
| Phân loại | Accuracy | `______` | 78% (S) / 70% (L) | Đạt / Không |
| | Macro-F1 | `______` | 0.74 (S) / 0.65 (L) | Đạt / Không |
| Truy hồi | Recall@5 | `______` | 0.78 (S) / 0.75 (L) | Đạt / Không |
| | Từ chối đúng | `______` | 1.0 mong muốn | Đạt / Không |
| Sinh văn bản | Trích dẫn hợp lệ | `______` | 95% (S) / 90% (L) | Đạt / Không |
| | Trích dẫn bịa | `______` | 0% | Đạt / Không |
| Vận hành | p50 | `______ ms` | — | |
| | p95 | `______ ms` | 30s (S) / 90s (L) | Đạt / Không |
| | Lời gọi model TB | `______` | ≤ 5 | Đạt / Không |
| An toàn | Chuyển người đúng | `______` | 92% (S) / 90% (L) | Đạt / Không |
| | Chuyển thừa | `______` | — | |
| | Ca đối kháng | `___/12` | 12/12 | Đạt / Không |

### 2b. Ma trận nhầm lẫn

```
              dự đoán →
thật ↓     cuoc  ket_noi  goi_cuoc  sim  thue_bao  khac
cuoc        ___    ___      ___     ___    ___     ___
ket_noi     ___    ___      ___     ___    ___     ___
goi_cuoc    ___    ___      ___     ___    ___     ___
sim         ___    ___      ___     ___    ___     ___
thue_bao    ___    ___      ___     ___    ___     ___
khac        ___    ___      ___     ___    ___     ___
```

**Cặp bị nhầm nhiều nhất: `____________` → `____________` (`___` ca)**

### 2c. Phân tích nguyên nhân ⚠︎ — phần quan trọng nhất buổi này

Liệt kê số **không phải** là phân tích. Trả lời ba câu:

**1. Hai nhóm này chồng lấn về ngữ nghĩa ở đâu?**
`___________________________________________________________________`

**2. Mở [`data/LABEL_GUIDE.md`](../data/LABEL_GUIDE.md). Ranh giới giữa hai nhóm đã được định nghĩa rõ chưa, hay chính định nghĩa nhãn mới là vấn đề?**
`___________________________________________________________________`
`___________________________________________________________________`

**3. Sửa được bằng prompt không? Nếu không thì cần sửa gì?**
`___________________________________________________________________`

> Bài học: **đôi khi vấn đề nằm ở định nghĩa nhãn chứ không nằm ở model.** Sửa model cho một vấn đề định nghĩa nhãn sẽ không bao giờ hiệu quả.

### 2d. MLflow

```bash
open http://localhost:5000
```
Run ID: `________________`  ·  `[ ]` đã ghi đủ tham số và chỉ số

---

## Bước 3 — Guardrails và 12 ca đối kháng · 25 phút

**`___:___` → `___:___`**

```bash
uv run python eval/run_eval.py --quick
```

| Mã | Loại | Vượt? | Nếu không — nguyên nhân và luật bổ sung |
|---|---|---|---|
| ADV-01 | chèn lệnh tiếng Việt | `[ ]` | `______________________` |
| ADV-02 | chèn lệnh tiếng Anh | `[ ]` | `______________________` |
| ADV-03 | chèn lệnh giấu trong ticket thật | `[ ]` | `______________________` |
| ADV-04 | dò hỏi thuê bao khác | `[ ]` | `______________________` |
| ADV-05 | giả danh nhân viên nội bộ | `[ ]` | `______________________` |
| ADV-06 | dụ cam kết bồi thường lớn | `[ ]` | `______________________` |
| ADV-07 | dụ cam kết bằng câu gợi sẵn | `[ ]` | `______________________` |
| ADV-08 | ngoài phạm vi tri thức | `[ ]` | `______________________` |
| ADV-09 | ngoài phạm vi, gần chủ đề có thật | `[ ]` | `______________________` |
| ADV-10 | ticket rác | `[ ]` | `______________________` |
| ADV-11 | nội dung xúc phạm | `[ ]` | `______________________` |
| ADV-12 | chứa PII, đòi nhắc lại PII | `[ ]` | `______________________` |

**Kết quả: `___/12`** — ngưỡng đạt là **12/12**.

> Ca chưa vượt được ưu tiên hoàn thành **cao hơn** trang theo dõi ở bước 4.

---

## Bước 4 — Truy vết, theo dõi, cổng chất lượng · 20 phút

**`___:___` → `___:___`**

### 4a. Tiêu chí truy vết ⚠︎ — điều kiện nghiệm thu của buổi

Chọn một mã ticket bất kỳ: `________________`

```bash
curl -s localhost:8000/trace/<trace_id> | jq
```

| Câu hỏi | Trả lời được? | Giá trị đọc được |
|---|---|---|
| Dùng prompt phiên bản nào? | `[ ]` | `______________` |
| Truy hồi ra đoạn nào, điểm bao nhiêu? | `[ ]` | `______________` |
| Gọi công cụ gì, tham số gì? | `[ ]` | `______________` |
| Guardrail nào kích hoạt? | `[ ]` | `______________` |
| Người duyệt đã làm gì? | `[ ]` | `______________` |
| Chạy ở cấu hình nào? | `[ ]` | `______________` |

> Không đáp ứng được bảng này thì hệ thống **chưa đạt mức sẵn sàng triển khai**, dù mọi tính năng đều chạy.

Kiểm luôn: nhật ký có lộ số thuê bao chưa che không? `[ ] không`  `[ ] có ⚠︎ phải sửa`

### 4b. Cổng chất lượng có thật sự CHẶN không

Cố tình hạ một ngưỡng trong `.github/workflows/ci.yml`, đẩy lên, xem CI.

CI có đỏ không? `[ ] Có — cổng hoạt động`  ·  `[ ] Không ⚠︎ cổng chỉ in cảnh báo, phải sửa`

Nhớ khôi phục ngưỡng: `[ ]`

---

## Bước 5 — Đo tải · 15 phút

**`___:___` → `___:___`**

```bash
CACHE_MODE=off uv run python scripts/bench_server.py
```

⚠︎ Quên `CACHE_MODE=off` là đang đo tốc độ đọc SQLite.

### Cấu hình L — cục bộ

| Đồng thời | p50 (s) | p95 (s) | Ticket/giờ | Lỗi |
|---|---|---|---|---|
| 1 | `______` | `______` | `______` | `___` |
| 3 | `______` | `______` | `______` | `___` |
| 5 | `______` | `______` | `______` | `___` |
| 10 | `______` | `______` | `______` | `___` |

### Cấu hình S — server, khe giờ `___:___ → ___:___`

| Đồng thời | p50 (s) | p95 (s) | Ticket/giờ | Lỗi |
|---|---|---|---|---|
| 1 | `______` | `______` | `______` | `___` |
| 5 | `______` | `______` | `______` | `___` |
| 10 | `______` | `______` | `______` | `___` |
| 20 | `______` | `______` | `______` | `___` |

**Điểm suy giảm — mức đồng thời mà p95 tăng đột biến: `______`**

Máy treo? Giảm đồng thời tối đa xuống 5. Mục tiêu là **quan sát quy luật suy giảm**, không phải tìm giới hạn tuyệt đối.

### Đối chiếu với Canvas ở Session 1 ⚠︎

Mở lại `WORKBOOK-1.md` ô 5.

| | Cấu hình L | Cấu hình S |
|---|---|---|
| Ticket/giờ đo được | `______` | `______` |
| Giả định trong Canvas | `______ ticket/ngày` ||
| Số giờ cần để xử lý khối lượng một ngày | `______ giờ` | `______ giờ` |
| **Giả định có đứng vững không?** | Có / Không | Có / Không |

**Nếu không khớp — con số nào sai, và sai bao nhiêu?**
`___________________________________________________________________`

> Đây là lúc con số kinh doanh viết ở buổi đầu gặp con số kỹ thuật đo được ở buổi cuối. Nếu chúng không khớp, một trong hai sai — và nhóm phải nói rõ là cái nào.

---

## Mốc kiểm tra cuối buổi · 5 phút

```bash
uv run pytest -m lab5
uv run python scripts/checkpoint.py 5 --team ______
```

Kết quả: `[ ] ĐỦ ĐIỀU KIỆN`  ·  `[ ] THIẾU ____/____`

### Nộp
- [ ] [`docs/EVALUATION.md`](../docs/EVALUATION.md) đủ 5 nhóm chỉ số, **mọi bảng ghi cấu hình**
- [ ] Bảng năng lực phục vụ **cả hai** cấu hình
- [ ] Phân tích lỗi chỉ ra **nguyên nhân**, không chỉ liệt kê số
- [ ] Kết quả 12 ca đối kháng
- [ ] Hệ thống khởi động bằng một lệnh từ máy sạch

## Chuẩn bị cho Session 6 ⚠︎

Chọn **đúng hai** cải tiến, dựa trên phân tích lỗi ở mục 2c — không theo cảm hứng.

| # | Cải tiến | Dựa trên phát hiện nào | Chỉ số kỳ vọng cải thiện |
|---|---|---|---|
| 1 | `______________________` | `______________________` | `______________` |
| 2 | `______________________` | `______________________` | `______________` |
