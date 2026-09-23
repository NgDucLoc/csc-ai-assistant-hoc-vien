# PHÂN ĐỊNH TRÁCH NHIỆM

Bàn giao không nêu rõ ai chịu trách nhiệm việc gì là bàn giao chưa hoàn tất. Bảng dưới đây phải được hai bên ký xác nhận trước khi nghiệm thu.

## 1. Ma trận trách nhiệm

| Hạng mục | Đơn vị phát triển | Đơn vị vận hành |
|---|---|---|
| Mã nguồn và kiến trúc | Chịu trách nhiệm | Không sửa trực tiếp |
| Sửa lỗi trong thời gian bảo hành | Chịu trách nhiệm | Báo lỗi kèm mã truy vết |
| Khởi động, dừng, khởi động lại dịch vụ | Hướng dẫn | Chịu trách nhiệm |
| Theo dõi chỉ số hàng ngày | Hướng dẫn | Chịu trách nhiệm |
| **Cập nhật kho tri thức khi chính sách đổi** | Hướng dẫn quy trình | **Chịu trách nhiệm** |
| Dựng lại chỉ mục sau khi sửa tri thức | Cung cấp công cụ | Chịu trách nhiệm |
| Chạy đánh giá định kỳ | Cung cấp công cụ | Chịu trách nhiệm |
| Hiệu chuẩn lại ngưỡng khi đổi model | Chịu trách nhiệm | Yêu cầu khi cần đổi |
| Sao lưu dữ liệu vận hành | Nêu danh mục cần sao lưu | Chịu trách nhiệm |
| Quyết định duyệt hay từ chối từng dự thảo | Không tham gia | **Chịu trách nhiệm hoàn toàn** |

## 2. Ranh giới trách nhiệm quan trọng nhất

**Mọi nội dung gửi tới khách hàng là trách nhiệm của người duyệt, không phải của hệ thống.**

Hệ thống soạn dự thảo. Giao dịch viên đọc, kiểm chứng theo các đoạn tri thức hiển thị bên trên dự thảo, rồi quyết định. Không có đường dẫn kỹ thuật nào cho phép bỏ qua bước này, và ranh giới đó phải được giữ nguyên trong mọi thay đổi về sau.

Hệ quả cho đơn vị vận hành: **giao dịch viên phải được đào tạo rằng dự thảo là bản nháp cần kiểm chứng, không phải câu trả lời đã được duyệt.** Một dự thảo viết trôi chảy và có trích dẫn đúng định dạng vẫn có thể sai.

## 3. Việc phải làm khi phát hiện hệ thống trả lời sai

| Bước | Ai làm | Trong bao lâu |
|---|---|---|
| Ghi nhận mã ticket và mã truy vết | Vận hành | Ngay |
| Tra nhật ký theo SC-02 trong `INCIDENTS.md` | Vận hành | 15 phút |
| Xác định mắt xích lỗi | Vận hành | 15 phút |
| Nếu lỗi ở tri thức: cập nhật tài liệu, dựng lại chỉ mục | Vận hành | 1 ngày làm việc |
| Nếu lỗi ở prompt, guardrail hoặc mã nguồn: chuyển phát triển | Phát triển | Theo cam kết bảo hành |
| Bổ sung ca kiểm thử để lỗi không lặp lại | Phát triển | Cùng lần sửa |

## 4. Cam kết bảo hành

| Hạng mục | Thời hạn | Ghi chú |
|---|---|---|
| Sửa lỗi chức năng | *điền* | Lỗi có mã truy vết tái hiện được |
| Hỗ trợ vận hành | *điền* | Kênh và giờ hỗ trợ |
| Hiệu chuẩn lại khi đổi model nền | *điền* | Bao gồm chạy lại toàn bộ bảng chỉ số |

## 5. Điều đơn vị vận hành cần biết mà tài liệu kỹ thuật chưa nói

Danh sách này trả lời trực tiếp câu hỏi phản biện *"Đơn vị vận hành nhận sản phẩm này vào thứ Hai. Họ cần biết những gì mà tài liệu của nhóm chưa nói?"*

1. **Sửa một tài liệu chính sách mà không dựng lại chỉ mục là lỗi im lặng.** Hệ thống không báo gì, chỉ trả lời theo bản cũ. Đây là lỗi vận hành nguy hiểm nhất và cũng dễ mắc nhất.
2. **Ngưỡng `RETRIEVE_MIN_SCORE` không được chỉnh tùy hứng.** Hạ ngưỡng làm hệ thống trả lời nhiều hơn nhưng bắt đầu bịa. Mỗi lần chỉnh phải chạy lại đánh giá và ghi vào nhật ký thay đổi.
3. **Số liệu chỉ có nghĩa khi kèm cấu hình.** Đổi từ cấu hình L sang S thì mọi ngưỡng cảnh báo phải đặt lại.
4. **Nút thắt là dịch vụ model.** Tăng `API_WORKERS` khi model đã bão hòa không tăng thông lượng, chỉ làm hàng đợi dài hơn.
5. **Tỉ lệ sửa của người duyệt là tín hiệu sớm nhất.** Nó báo trước điểm đánh giá tự động vài tuần, vì tập kiểm định cố định còn ticket thật thì không.

## 6. Xác nhận

| | Đơn vị phát triển | Đơn vị vận hành |
|---|---|---|
| Người đại diện | | |
| Chức vụ | | |
| Ngày | | |
| Chữ ký | | |
