# LAB 6 — Final AI Application

**Session 6 · Ngày 3, buổi chiều · 180 phút thực hành · Deliverable: sản phẩm hoàn chỉnh + demo**

> **Chỗ ghi chép:** sao chép [`workbooks/WORKBOOK-6.md`](../workbooks/WORKBOOK-6.md) vào `docs/workbook/<tên-nhóm>-session-6.md` và điền trong giờ học. Đề bài này nói *phải làm gì*; workbook là chỗ ghi *đã đo được gì và vì sao chọn như vậy* — phần phản biện ở Session 6 hỏi đúng phần đó.

---

## Bước 1 — Sprint cải tiến (55 phút)

Chọn **đúng hai** cải tiến, dựa trên phân tích lỗi ở Session 5. Không theo cảm hứng.

> **Giới hạn đúng hai là có chủ ý.** Nó buộc phải xếp thứ tự ưu tiên bằng dữ liệu, và bảo đảm còn đủ thời gian đo lại. Nhóm làm năm cải tiến rồi không kịp đo cái nào sẽ không có gì để trình bày.

### Quy tắc

**Mỗi lần chỉ thay đổi một biến.** Thay đổi nhiều thứ cùng lúc rồi báo kết quả tốt lên thì không quy được kết quả cho nguyên nhân nào.

### Đo lại bằng đúng bộ chỉ số cũ

```bash
uv run python eval/run_eval.py --background &
```

So sánh trên MLflow tại `localhost:5000`.

### Bảng cần điền

| # | Cải tiến | Dựa trên phát hiện nào ở Session 5 | Chỉ số trước | Chỉ số sau | Cấu hình |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |

**Sản phẩm:** bảng cải tiến có số liệu trước sau.

---

## Bước 2 — Model Card và gói bàn giao (25 phút)

### 2a. Kiểm tra thiên lệch

```bash
uv run python scripts/bias_check.py
```

Câu hỏi: **hệ thống có xử lý khác nhau giữa các nhóm khách hàng không?** Ba chiều đo được: văn phong, sắc thái, kênh tiếp nhận.

Chênh lệch trên 15 điểm phần trăm là **một giới hạn phải ghi vào Model Card, không phải con số để giấu đi**.

Lưu ý giới hạn của chính phép đo: tập kiểm định 40 ticket, một số nhóm dưới 5 ca. Chênh lệch trên nhóm dưới 5 ca chưa đủ căn cứ kết luận — và phải nói rõ điều đó.

### 2b. Model Card

Điền [`docs/MODEL_CARD.md`](../docs/MODEL_CARD.md): mục đích sử dụng, phạm vi áp dụng, **giới hạn đã biết**, kết quả đánh giá, rủi ro đã lường trước.

> **Mục "Giới hạn đã biết" để trống là không chấp nhận được.** Tối thiểu ba giới hạn cụ thể, rút ra từ phân tích lỗi ở Session 5. Viết chung chung kiểu "hệ thống có thể sai trong một số trường hợp" không tính.

Model Card là **một phần của hồ sơ nghiệm thu**, không phải tài liệu trang trí.

### 2c. Gói bàn giao

| Tệp | Nội dung |
|---|---|
| `docs/handover/RUNBOOK.md` | Dựng lại hệ thống, thao tác hàng ngày, cập nhật tri thức |
| `docs/handover/INCIDENTS.md` | Ba sự cố thường gặp, cách xử lý ngay và tận gốc |
| `docs/handover/RESPONSIBILITIES.md` | Ai chịu trách nhiệm việc gì |

> Bàn giao thiếu sổ tay vận hành là nguyên nhân phổ biến nhất khiến sản phẩm chết sau nghiệm thu.

**Sản phẩm:** Model Card và gói bàn giao.

---

## Bước 3 — Chuẩn bị trình diễn (30 phút)

### Kịch bản 8 phút

| Phút | Nội dung |
|---|---|
| 0–1 | Bài toán và phạm vi |
| 1–2 | Kiến trúc 5 tầng |
| 2–6 | **Bốn kịch bản demo** |
| 6–7 | Kết quả đánh giá và hai cải tiến |
| 7–8 | Giới hạn đã biết và hướng phát triển |

### Bốn ticket demo, chuẩn bị sẵn

1. Một ca xử lý trơn tru
2. Một ca phải gọi công cụ
3. Một ca bị chuyển người
4. **Một ca đối kháng bị chặn**

### Video dự phòng — bắt buộc

Quay sẵn toàn bộ demo. **Khi cả lớp cùng chạy model vào giờ trình diễn, tốc độ có thể chậm bất thường.** Yêu cầu này không phải hình thức.

**Sản phẩm:** kịch bản, slide ~10 trang, video dự phòng.

---

## Bước 4 — Trình bày và phản biện (60 phút)

Mỗi nhóm 8 phút trình diễn + 5 phút hỏi đáp. Nhóm khác **bắt buộc đặt tối thiểu một câu hỏi**.

### Trình bày QUYẾT ĐỊNH THIẾT KẾ, không phải tính năng

Cách trình bày một quyết định:

```
Bối cảnh → Các phương án đã cân nhắc → Tiêu chí lựa chọn → Hệ quả chấp nhận
```

Tài liệu dùng để bảo vệ chính là **bảng quyết định thiết kế đã lập từ Session 2** và các ADR.

### Ngân hàng câu hỏi phản biện

Chuẩn bị trước câu trả lời cho:

| Nhóm | Câu hỏi |
|---|---|
| Quyết định thiết kế | Vì sao chọn kích thước đoạn như vậy? Đã thử phương án nào khác, kết quả ra sao? |
| Quyết định thiết kế | Ngưỡng chuyển người dựa trên căn cứ gì? Hạ ngưỡng thì đánh đổi là gì? |
| Khả năng mở rộng | Lưu lượng tăng gấp mười thì nút thắt ở đâu? Xử lý thế nào? |
| Khả năng mở rộng | Hệ thống phục vụ được bao nhiêu ticket mỗi giờ? Đủ cho khối lượng giả định trong Canvas không? |
| Trách nhiệm | Hệ thống có xử lý khác nhau giữa các nhóm khách hàng không? Kiểm chứng bằng cách nào? |
| Bàn giao | Đơn vị vận hành nhận sản phẩm vào thứ Hai. Họ cần biết gì mà tài liệu chưa nói? |
| Vận hành | Hệ thống trả lời sai một khách hàng. Truy vết nguyên nhân bằng cách nào, mất bao lâu? |
| An toàn | Trường hợp nào hệ thống có thể gây rủi ro nghiệp vụ? Đã có biện pháp gì? |
| Đánh giá | Con số báo cáo đo trên tập nào, cấu hình nào? Chạy lại có ra tương tự không? |
| Triển khai | Phải đưa lên môi trường thật tuần sau, ba việc làm trước tiên là gì? |
| Giới hạn | Đâu là điều hệ thống chắc chắn không làm được? Biết điều đó bằng cách nào? |

**Sản phẩm:** biên bản phản biện.

---

## Bước 5 — Tổng kết (10 phút)

Giảng viên hệ thống lại các quyết định kiến trúc các nhóm đã đưa ra, chỉ ra điểm khác biệt và giải thích **vì sao nhiều lựa chọn khác nhau vẫn có thể cùng đúng tùy bối cảnh**.

---

## Nộp sau buổi học

- Hệ thống hoàn chỉnh trên nhánh nhóm, qua pull request đã được nhóm khác duyệt
- Slide ~10 trang: bài toán, kiến trúc, quyết định thiết kế, kết quả đánh giá, hướng phát triển
- Gói bàn giao: README dựng lại hệ thống, sổ tay vận hành, quy trình xử lý sự cố
- Model Card kèm kết quả kiểm tra thiên lệch
- Bảng so sánh trước sau của hai cải tiến

## Tự kiểm tra

```bash
uv run pytest
uv run python scripts/checkpoint.py 6
```

## Thang điểm (10)

| Tiêu chí | Điểm |
|---|---|
| Hai cải tiến thực hiện và đo lại đúng phương pháp | 2 |
| Model Card đầy đủ, có kết quả kiểm tra thiên lệch | 2 |
| Trình diễn đủ bốn tình huống | 2 |
| Trình bày và **bảo vệ được quyết định thiết kế** | 2 |
| Gói bàn giao đủ để đơn vị vận hành tiếp nhận và xử lý sự cố | 2 |

## Lỗi thường gặp

| Tình huống | Cách xử lý |
|---|---|
| Thay đổi nhiều thứ cùng lúc rồi báo kết quả tốt lên | Không quy được kết quả cho nguyên nhân nào. Tách ra, đo lại từng thay đổi |
| Trình bày tính năng thay vì quyết định thiết kế | Chuyển hướng: vì sao chọn như vậy, đã loại phương án nào |
| Hệ thống chạy chậm hoặc lỗi lúc trình diễn | Chuyển sang video dự phòng. Phần hỏi đáp vẫn diễn ra bình thường |
| Model Card viết chung chung, mục giới hạn để trống | Không chấp nhận. Tối thiểu ba giới hạn cụ thể từ phân tích lỗi Session 5 |

---

## Về việc dùng trợ lý lập trình AI

Học viên được phép dùng trợ lý lập trình AI trong quá trình thực hành, với hai ràng buộc:

1. **Phải giải thích được mọi dòng mã trong bài nộp.** Phần phản biện ở bước 4 kiểm tra điều này.
2. **Phần thiết kế do học viên tự quyết định:** Canvas, Blueprint, ADR, điều kiện chuyển người, luật guardrail. Trợ lý AI có thể hỗ trợ diễn đạt nhưng không thay thế quyết định thiết kế.

Câu hỏi thảo luận 10 phút: **điều gì thay đổi trong khâu rà soát mã và kiểm thử khi phần lớn mã do AI sinh ra?** Gợi ý: cổng chất lượng tự động trở nên quan trọng hơn chứ không kém đi.
