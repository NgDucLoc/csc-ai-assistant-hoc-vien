# LAB 4 — AI Prototype v1

**Session 4 · Ngày 2, buổi chiều · 120 phút thực hành · Deliverable: prototype chạy thông**

> **Đây là buổi dễ vỡ nhất toàn khóa.** Nó dựa trực tiếp lên phần RAG làm sáng nay và không có đêm để bù. Nếu `checkpoint.py 3` chưa PASS, chạy `./scripts/rescue.sh 3` **trước khi bắt đầu**, đừng cố làm bù.

## Bước 0 — Rà soát chéo (10 phút)

Đổi pull request với nhóm bạn. Checklist rà soát:

- [ ] Prompt có đủ 5 phần và có phân tách `<ticket>` không?
- [ ] Bốn lớp phòng vệ có đủ, đặc biệt lớp 3 có đưa lỗi vào prompt không?
- [ ] Truy hồi có lọc `status: superseded` không?
- [ ] Bảng số liệu có cột cấu hình không?
- [ ] Có chỗ nào gọi model ngoài [`src/llm/client.py`](../src/llm/client.py) không?

Approve rồi merge. Bấm approve cho xong là bỏ mất giá trị của bước này.

> **Chỗ ghi chép:** sao chép [`workbooks/WORKBOOK-4.md`](../workbooks/WORKBOOK-4.md) vào `docs/workbook/<tên-nhóm>-session-4.md` và điền trong giờ học. Đề bài này nói *phải làm gì*; workbook là chỗ ghi *đã đo được gì và vì sao chọn như vậy* — phần phản biện ở Session 6 hỏi đúng phần đó.

---

## Bước 1 — Thiết kế quy trình TRÊN GIẤY trước khi viết mã (30 phút)

Vẽ sơ đồ luồng đầy đủ **với các nhánh rẽ**. Không chỉ luồng thuận lợi.

Liệt kê **tối thiểu bốn điều kiện bắt buộc chuyển người**, mỗi điều kiện kèm lý do.

Gợi ý nếu bí:

- Độ tin cậy phân loại thấp
- Không tìm được căn cứ trong kho tri thức
- Khách hàng yêu cầu bồi thường tiền
- Ticket ở mức ưu tiên cao nhất
- Khách hàng có dấu hiệu sẽ khiếu nại lên cấp trên

**Sản phẩm:** sơ đồ luồng và danh sách điều kiện chuyển người.

---

## Bước 2 — Gọi công cụ và đường dự phòng theo luật (30 phút)

### 2a. Ba công cụ giả lập

| Công cụ | Tham số | Trả về |
|---|---|---|
| `get_subscriber_info` | `subscriber_id` | Gói cước, ngày kích hoạt, trạng thái |
| `get_billing_history` | `subscriber_id`, `months` | Cước 6 tháng gần nhất |
| `check_area_incident` | `area_code`, `date` | Có/không sự cố hạ tầng |

Ràng buộc bắt buộc: **chỉ đọc**, timeout 5 giây, tối đa 3 lần gọi mỗi ticket, **tham số được validate trước khi thực thi**.

### 2b. Đường dự phòng theo luật

Model 3B gọi công cụ không ổn định — có lúc quên gọi, có lúc sai tham số, có lúc bịa tên công cụ. Cài bảng luật:

| Điều kiện | Công cụ gọi tự động |
|---|---|
| `cuoc_thanh_toan` + có `subscriber_id` | `get_billing_history` |
| `chat_luong_ket_noi` + có `subscriber_id` | `check_area_incident` |
| Mọi ticket có `subscriber_id` hợp lệ | `get_subscriber_info` |

> **Việc phải xây đường dự phòng cho quyết định của model là một nguyên tắc thiết kế, không phải một sự thỏa hiệp kỹ thuật.** Mọi quyết định do model đưa ra trong hệ thống production đều cần một đường lùi tất định.

**Sản phẩm:** ba công cụ hoạt động, có đường dự phòng.

---

## Bước 3 — Sinh phản hồi có căn cứ và ghép quy trình (35 phút)

### 3a. Ràng buộc bắt buộc trong prompt sinh phản hồi

1. Chỉ dùng thông tin trong ngữ cảnh
2. Mỗi khẳng định về chính sách kèm trích dẫn `[KB-xxx vN, hiệu lực YYYY-MM-DD]`
3. **Không cam kết bồi thường hay số tiền cụ thể** trừ khi có nguyên văn trong ngữ cảnh
4. Không hứa mốc thời gian nếu ngữ cảnh không nêu
5. Không nhắc PII, không nhắc thuê bao khác
6. **Không đủ căn cứ → trả `KHÔNG ĐỦ CĂN CỨ`, không viết gì thêm**

### 3b. Ghép toàn bộ và chạy thử 5 ticket đa dạng

Chọn 5 ticket khác nhau về nhóm, mức ưu tiên và độ khó. **Bao gồm một ticket rác** — hệ thống phải chuyển người có kiểm soát, không văng lỗi.

**Sản phẩm:** quy trình chạy thông từ đầu tới cuối.

---

## Bước 4 — Màn hình duyệt và nhật ký thao tác (25 phút)

Giao diện hiển thị theo **đúng thứ tự này**:

1. Ticket gốc
2. Kết quả phân loại
3. **Các đoạn tri thức đã truy hồi**
4. Dự thảo phản hồi

> Đặt dự thảo lên đầu là sai. Người duyệt sẽ đọc dự thảo rồi tìm cách biện minh cho nó thay vì kiểm chứng nó, và thao tác duyệt mất hết giá trị làm tín hiệu chất lượng.

Ba lựa chọn: **duyệt** · **sửa rồi duyệt** · **từ chối kèm lý do**. Mọi thao tác ghi vào cơ sở dữ liệu.

> **Nhật ký thao tác duyệt không phải để giao diện trông đầy đủ.** Tỉ lệ sửa và lý do từ chối là chỉ số chất lượng đáng tin cậy nhất mà hệ thống có, và là nguồn dữ liệu chính cho sprint cải tiến ở Session 6.

**Nếu thiếu thời gian:** ưu tiên hoàn thành phần ghi nhật ký, phần giao diện có thể đơn giản hóa.

**Sản phẩm:** màn hình duyệt và nhật ký thao tác.

---

## Nộp sau buổi học

- Prototype chạy được từ đầu tới cuối
- **Video quay màn hình ~2 phút**, ba tình huống: một ca trơn tru, một ca phải gọi công cụ, một ca bị chuyển người
- Sơ đồ luồng cập nhật, phản ánh đúng những gì đã cài đặt

## Tự kiểm tra

```bash
uv run pytest -m lab4
uv run python scripts/checkpoint.py 4
```

## Thang điểm (10)

| Tiêu chí | Điểm |
|---|---|
| Quy trình chạy thông trên các ticket thử nghiệm | 3 |
| Gọi công cụ hoạt động, có đường dự phòng | 2 |
| ≥ 4 điều kiện chuyển người, đã cài đặt và kiểm chứng | 2 |
| Màn hình duyệt hoạt động, ghi được nhật ký | 2 |
| Video đủ ba tình huống | 1 |

## Lỗi thường gặp

| Tình huống | Cách xử lý |
|---|---|
| Chỉ ghép được luồng thuận lợi | Gửi một ticket rác. Phải chuyển người có kiểm soát, không dừng vì lỗi |
| Model gọi công cụ sai tham số | Đây là hành vi đã dự liệu. Kích hoạt đường dự phòng và **ghi nhận tỉ lệ** để phân tích ở Session 5 |
| Sinh phản hồi ngay cả khi không có căn cứ | **Lỗi nghiêm trọng.** Cài lại quy tắc từ chối — đây là ranh giới an toàn quan trọng nhất |

## Nếu xong sớm

Cài vòng lặp agent thực thụ cho nhánh xử lý phức tạp: model tự lập kế hoạch, chọn công cụ, quan sát kết quả, quyết định bước tiếp theo — **có giới hạn số vòng lặp**.
