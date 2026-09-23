# HƯỚNG DẪN GÁN NHÃN TICKET

Tài liệu này được viết **trước khi gán nhãn**, không phải sau. Nhãn gán mà không có hướng dẫn thống nhất sẽ nhiễu, và mọi chỉ số ở Lab 5 đo trên nhãn nhiễu đều vô nghĩa.

Quy trình đã áp dụng khi dựng bộ dữ liệu: hai người gán độc lập 20 ticket đầu, đo mức đồng thuận, chỉnh hướng dẫn này, rồi mới gán nốt 100 ticket còn lại.

---

## 1. Nhóm vấn đề

Chọn đúng một nhóm. Khi ticket chạm nhiều nhóm, hỏi: **khách hàng thực sự muốn gì sau khi đọc xong phản hồi?**

| Mã | Chọn khi |
|---|---|
| `cuoc_thanh_toan` | Khách hàng nói về **số tiền đã bị trừ** hoặc **hóa đơn đã phát hành**. Có tranh chấp tiền. |
| `chat_luong_ket_noi` | Vấn đề về **trải nghiệm dùng dịch vụ**: mất sóng, chậm, rớt. |
| `goi_cuoc_khuyen_mai` | Hỏi về **điều khoản của gói hoặc chương trình**, chưa phát sinh tranh chấp tiền. |
| `thiet_bi_sim` | Về SIM, thiết bị đầu cuối, cấu hình máy, trạng thái khóa thuê bao. |
| `thong_tin_thue_bao` | Về thông tin định danh, hợp đồng, chuyển nhượng, chuẩn hóa. |
| `khac` | Góp ý, hỏi thông tin chung, nội dung vô nghĩa. |

### Ranh giới hay nhầm nhất

**`cuoc_thanh_toan` với `goi_cuoc_khuyen_mai`.** Đây là cặp gây nhầm lẫn nhiều nhất, và đó là chủ ý — Session 5 dùng chính cặp này để dạy đọc ma trận nhầm lẫn.

Quy tắc phân định: **đã mất tiền chưa?**

- *"Đăng ký gói 5G mà bị trừ tiền gói cũ"* → `cuoc_thanh_toan`. Có nhắc gói, nhưng tiền đã mất.
- *"Gói 5G có bao nhiêu GB?"* → `goi_cuoc_khuyen_mai`. Chưa có giao dịch nào.
- *"Nạp tiền đợt khuyến mãi mà không được cộng"* → `goi_cuoc_khuyen_mai`. Tranh chấp về **ưu đãi chưa nhận**, không phải về **tiền đã bị trừ sai**.

**`chat_luong_ket_noi` với `thiet_bi_sim`.** Quy tắc: nguyên nhân nằm ở **mạng** hay ở **máy và SIM**?

- *"Cả xóm mất sóng"* → `chat_luong_ket_noi`.
- *"Máy tôi không có sóng, máy vợ tôi cùng chỗ vẫn đầy"* → `thiet_bi_sim`.
- Nếu ticket không đủ thông tin để phân định, đánh dấu `is_ambiguous` và chọn nhóm theo biểu hiện khách hàng mô tả.

---

## 2. Mức ưu tiên

| Mức | Chọn khi |
|---|---|
| `P1` | Mất dịch vụ hoàn toàn · ảnh hưởng hoạt động doanh nghiệp · khách hàng đe dọa khiếu nại lên cơ quan quản lý hoặc báo chí |
| `P2` | Ảnh hưởng trải nghiệm rõ rệt · có tranh chấp tiền |
| `P3` | Yêu cầu thông tin · thao tác thông thường |

**Lưu ý:** giọng điệu gay gắt **không** tự động nâng mức ưu tiên. Một khách hàng chửi mắng vì hỏi cú pháp tra cứu vẫn là `P3`. Trộn hai chiều này là lỗi gán nhãn phổ biến nhất.

---

## 3. Sắc thái

| Mức | Dấu hiệu |
|---|---|
| `trung_tinh` | Trình bày sự việc, hỏi thông tin |
| `buc_boi` | Có thể hiện khó chịu, nhưng còn hợp tác |
| `gay_gat` | Yêu cầu dứt khoát, đe dọa, hoặc có lời lẽ nặng |

---

## 4. Trường `meta`

| Trường | Ý nghĩa |
|---|---|
| `is_ambiguous` | Ticket gán được hai nhãn một cách hợp lý. Dùng để kiểm chứng ngưỡng tin cậy — hệ thống **phải** hạ độ tin cậy ở các ca này. |
| `has_pii` | Ticket chứa thông tin cá nhân nhạy cảm cần che. |
| `is_junk` | Nội dung vô nghĩa. Phải bị chặn ở guardrail đầu vào. |
| `expected_action` | `auto_draft` hoặc `escalate`. Dùng để đo tỉ lệ chuyển người đúng. |
| `note` | Lý do gán nhãn với ca khó. Bắt buộc điền khi `is_ambiguous=true`. |

---

## 5. Nguyên tắc bất di bất dịch

Toàn bộ dữ liệu là **dữ liệu sinh tổng hợp**. Nghiêm cấm đưa dữ liệu khách hàng thật, dữ liệu nội bộ chưa được phê duyệt công bố, hoặc thông tin định danh cá nhân thật vào repo — kể cả trong tệp kiểm thử hoặc ảnh chụp màn hình nộp bài.

Số thuê bao trong dữ liệu dùng dải `098700xxxx` không tồn tại thực tế, và được che một phần trong mọi hiển thị.

Hook `pre-commit` chặn số điện thoại có thật lọt vào repo. Hook đó là hàng rào cuối, không phải hàng rào đầu tiên — trách nhiệm vẫn ở người soạn dữ liệu.
