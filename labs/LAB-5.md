# LAB 5 — Production-ready Prototype

**Session 5 · Ngày 3, buổi sáng · 120 phút thực hành · Deliverable: [`docs/EVALUATION.md`](../docs/EVALUATION.md) + hệ thống đóng gói**

> **Đọc mục "Việc chạy nền" bên dưới TRƯỚC khi bắt đầu.** Hai việc phải khởi động ngay phút đầu, nếu không sẽ vỡ giờ.

## Việc phải khởi động ngay phút đầu

### 1. Chạy đánh giá dưới nền

Đánh giá 40 ticket trên CPU mất nhiều thời gian hơn 30 phút của bước 2. Khởi động ngay:

```bash
uv run python eval/run_eval.py --background &
watch -n5 cat eval/results/progress.json
```

Không để cả nhóm ngồi nhìn thanh tiến trình. Làm bước 1 trong lúc chờ.

### 2. Ghi nhớ khe giờ đo tải trên server

Sáu nhóm cùng đo trên một server sẽ làm số liệu của nhau nhiễu tới mức không dùng được. Giảng viên phát **bảng phân khe giờ 5 phút mỗi nhóm, trải suốt buổi sáng**.

Khe của nhóm bạn: `________`

`bench_server.py` tự từ chối chạy sai khe. Đó là chủ ý, không phải lỗi.

> **Chỗ ghi chép:** sao chép [`workbooks/WORKBOOK-5.md`](../workbooks/WORKBOOK-5.md) vào `docs/workbook/<tên-nhóm>-session-5.md` và điền trong giờ học. Đề bài này nói *phải làm gì*; workbook là chỗ ghi *đã đo được gì và vì sao chọn như vậy* — phần phản biện ở Session 6 hỏi đúng phần đó.

---

## Bước 1 — API bất đồng bộ và đóng gói (30 phút)

### 1a. Vì sao phải bất đồng bộ

Mỗi ticket mất hàng chục giây. Mô hình đồng bộ — client gửi rồi chờ kết quả — không hợp lệ với độ trễ đó. Hợp đồng phải là **"nhận việc"**, không phải "trả kết quả".

| Điểm cuối | Vai trò |
|---|---|
| `POST /tickets` | Trả `job_id` ngay, HTTP 202 |
| `GET /jobs/{id}` | Tra trạng thái và kết quả |
| `GET /review/queue` | Hàng đợi chờ duyệt |
| `POST /review/{job_id}` | Ghi thao tác duyệt |
| `GET /trace/{trace_id}` | Tái dựng vòng đời một ticket |
| `GET /health`, `GET /metrics` | Sức khỏe và chỉ số |

**Trạng thái nằm ngoài tiến trình** (SQLite), không giữ trong bộ nhớ worker. Worker khởi động lại không mất việc đang chờ, và tầng API mở rộng ngang được độc lập với tầng xử lý.

Kiểm tra tài liệu API tự sinh tại `http://localhost:8000/docs`.

### 1b. Đóng gói

```bash
docker compose up --build
```

Ba dịch vụ: `api`, `ui`, `mlflow`. **Dịch vụ model đặt ngoài container** — xem [ADR-0004](../docs/adr/0004-dich-vu-model-ngoai-container.md) cho lý do.

**Nếu Docker lỗi trên Windows:** chạy trực tiếp các dịch vụ. Phần đóng gói được chấm qua tệp cấu hình đã viết, vì nút thắt nằm ở Docker Desktop chứ không ở thiết kế của nhóm.

**Sản phẩm:** hệ thống bất đồng bộ khởi động bằng một lệnh.

---

## Bước 2 — Đọc kết quả đánh giá và phân tích lỗi (30 phút)

Kết quả từ lệnh chạy nền lúc đầu buổi giờ đã có. Đây là **thời gian phân tích, không phải thời gian chờ**.

### 2a. Điền năm nhóm chỉ số vào `docs/EVALUATION.md`

Mọi bảng **bắt buộc ghi cấu hình đã dùng**.

### 2b. Đọc ma trận nhầm lẫn

Trả lời: **nhóm vấn đề nào bị nhầm nhiều nhất, và vì sao?**

> Kết quả thường gặp: `cuoc_thanh_toan` bị nhầm với `goi_cuoc_khuyen_mai`, do hai nhóm chồng lấn về ngữ nghĩa. Từ đó rút ra bài học: **đôi khi vấn đề nằm ở định nghĩa nhãn chứ không nằm ở model.** Mở [`data/LABEL_GUIDE.md`](../data/LABEL_GUIDE.md) và kiểm tra ranh giới đã được định nghĩa rõ chưa.

Phân tích không phải là liệt kê số. Với mỗi cặp nhầm nhiều nhất, trả lời ba câu trong mục 3 của `EVALUATION.md`.

### 2c. Ghi lần chạy vào MLflow

```bash
open http://localhost:5000
```

So sánh với các lần chạy trước. Không có manifest thì con số không có giá trị so sánh, vì không biết nó thuộc về cấu hình nào.

**Sản phẩm:** bảng số liệu, lần chạy trên MLflow, phân tích lỗi.

---

## Bước 3 — Guardrails ba lớp và bộ ca đối kháng (25 phút)

| Lớp | Chặn cái gì |
|---|---|
| Đầu vào | Chèn lệnh, thông tin cá nhân, ticket rác |
| Đầu ra | Cam kết tiền không căn cứ, trích dẫn bịa, rò rỉ PII, hứa mốc thời gian |
| Vận hành | Ngắt mạch, ngân sách gọi model, suy giảm có kiểm soát |

Kiểm chứng bằng 12 ca đối kháng:

```bash
uv run python eval/run_eval.py --quick
```

12 ca gồm: chèn lệnh (3), dò hỏi thuê bao khác (2), dụ cam kết bồi thường (2), ngoài phạm vi tri thức (2), ticket rác (1), nội dung xúc phạm (1), chứa PII (1).

**Ngưỡng đạt là 12/12.** Ca chưa vượt: phân tích nguyên nhân và bổ sung luật. **Phần này được ưu tiên cao hơn trang theo dõi ở bước 4.**

**Sản phẩm:** kết quả 12 ca đối kháng.

---

## Bước 4 — Nhật ký, theo dõi, cổng chất lượng (20 phút)

### 4a. Kiểm chứng tiêu chí truy vết

Chọn một mã ticket bất kỳ và tái dựng:

```bash
curl -s localhost:8000/trace/<trace_id> | jq
```

Phải trả lời được đủ sáu câu:

| Câu hỏi | Có trả lời được? |
|---|---|
| Dùng prompt phiên bản nào? | |
| Truy hồi ra đoạn nào, điểm bao nhiêu? | |
| Gọi công cụ gì, tham số gì? | |
| Guardrail nào kích hoạt? | |
| Người duyệt đã làm gì? | |
| Chạy ở cấu hình nào? | |

> **Không đáp ứng được bảng này thì hệ thống chưa đạt mức sẵn sàng triển khai**, dù mọi tính năng đều chạy.

### 4b. Trang theo dõi

Hiển thị tỉ lệ sửa và tỉ lệ từ chối của người duyệt — **tín hiệu phát hiện suy giảm chất lượng sớm nhất mà hệ thống có**, sớm hơn cả điểm đánh giá tự động.

### 4c. Bật đủ bốn giai đoạn CI kèm ngưỡng chặn

Kiểm chứng cổng **thật sự chặn**, không chỉ in cảnh báo: cố tình hạ một ngưỡng trong `.github/workflows/ci.yml`, đẩy lên, xem CI có đỏ không.

**Sản phẩm:** nhật ký, trang theo dõi, CI có cổng chất lượng.

---

## Bước 5 — Đo tải trên cấu hình cục bộ (15 phút)

```bash
CACHE_MODE=off uv run python scripts/bench_server.py
```

Đo ở các mức đồng thời 1, 3, 5, 10.

**Nếu máy treo:** giảm mức đồng thời tối đa xuống 5. Mục tiêu là quan sát **quy luật suy giảm**, không phải tìm giới hạn tuyệt đối của máy.

Phần đo trên server đã làm ở khe giờ riêng trong buổi sáng.

### Đối chiếu với Canvas

Điền mục 5 của `EVALUATION.md`: hệ thống phục vụ được bao nhiêu ticket mỗi giờ ở mỗi cấu hình? Con số đó có đủ cho khối lượng đã giả định trong Canvas ở Session 1 không?

> Đây là lúc con số kinh doanh viết ở buổi đầu gặp con số kỹ thuật đo được ở buổi cuối. Nếu chúng không khớp, một trong hai sai — và nhóm phải nói rõ là cái nào.

**Sản phẩm:** bảng năng lực phục vụ hai cấu hình.

---

## Nộp sau buổi học

- [`docs/EVALUATION.md`](../docs/EVALUATION.md) đầy đủ 5 nhóm chỉ số, bảng năng lực hai cấu hình, phân tích lỗi, đề xuất cải tiến. **Mọi bảng ghi rõ cấu hình.**
- Hệ thống khởi động được bằng một lệnh từ máy sạch
- Kết quả bộ 12 ca đối kháng

## Tự kiểm tra

```bash
uv run pytest -m lab5
uv run python scripts/checkpoint.py 5
```

## Thang điểm (10)

| Tiêu chí | Điểm |
|---|---|
| Hệ thống bất đồng bộ, đóng gói, khởi động từ máy sạch | 2 |
| Đủ 5 nhóm chỉ số, ghi được vào MLflow | 3 |
| Phân tích lỗi **chỉ ra nguyên nhân**, không chỉ liệt kê số | 2 |
| Guardrails vượt toàn bộ 12 ca đối kháng | 2 |
| Truy vết được ticket bất kỳ, CI có cổng, có số liệu hai cấu hình | 1 |

## Lỗi thường gặp

| Tình huống | Cách xử lý |
|---|---|
| Báo cáo số liệu không kèm cấu hình | Không chấp nhận. Không có manifest thì con số không so sánh được |
| Chạy đánh giá nhầm trên tập huấn luyện | Chạy lại. Lỗi này làm sai lệch toàn bộ kết luận |
| Vài ca đối kháng chưa vượt | Phân tích nguyên nhân, bổ sung luật. Ưu tiên cao hơn trang theo dõi |
| Số liệu lẫn giữa hai cấu hình | Kiểm tra `config_profile` trong log. Xóa cache của cấu hình sai rồi chạy lại |
| Chạy đo tải ngoài khe giờ được phân | Số đo bị nhiễu, không dùng được. Đo lại đúng khe hoặc chỉ báo cáo số cục bộ kèm ghi chú |

## Nếu xong sớm

So sánh A/B hai phiên bản prompt trên cùng tập kiểm định, và **kiểm định ý nghĩa thống kê của chênh lệch** thay vì chỉ so sánh con số trung bình. Với n=40, chênh lệch 3 điểm phần trăm có thể chỉ là nhiễu.
