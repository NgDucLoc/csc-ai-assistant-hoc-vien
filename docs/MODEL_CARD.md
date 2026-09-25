# MODEL CARD — Trợ lý xử lý ticket CSKH viễn thông

> Model Card là **một phần của hồ sơ nghiệm thu**, không phải tài liệu trang trí. Đơn vị vận hành đọc tài liệu này để biết hệ thống làm được gì, không làm được gì, và trong hoàn cảnh nào nó sai.
>
> Phần *Giới hạn đã biết* để trống là không chấp nhận được. Tối thiểu ba giới hạn cụ thể, rút ra từ phân tích lỗi ở Session 5.

| | |
|---|---|
| Tên hệ thống | `csc-ai-assistant` |
| Phiên bản | *điền* |
| Ngày phát hành | *điền* |
| Đơn vị phát triển | *điền tên nhóm* |
| Cấu hình tham chiếu | *điền S hoặc L* |
| Model nền | *điền* |
| Model embedding | `bge-m3` |

---

## 1. Mục đích sử dụng

**Được dùng để:** hỗ trợ giao dịch viên tuyến một phân loại ticket, tra cứu chính sách liên quan, và soạn dự thảo phản hồi. Mọi dự thảo phải qua thao tác duyệt của con người trước khi tới khách hàng.

**Không được dùng để:**

- Gửi phản hồi tự động tới khách hàng.
- Ra quyết định nghiệp vụ có ràng buộc tài chính — bồi thường, hoàn cước, miễn phí.
- Thay thế giao dịch viên trong các tình huống thuộc diện bắt buộc chuyển tuyến theo KB-027.
- Xử lý ticket bằng ngôn ngữ khác tiếng Việt.

## 2. Phạm vi áp dụng

| Chiều | Phạm vi |
|---|---|
| Ngôn ngữ | Tiếng Việt |
| Miền nghiệp vụ | Chăm sóc khách hàng viễn thông, 6 nhóm vấn đề |
| Kho tri thức | 28 tài liệu chính sách nội bộ, có ngày hiệu lực |
| Kênh | Ticket dạng văn bản từ app, tổng đài, thư điện tử |
| Ngoài phạm vi | Giọng nói, hình ảnh, tệp đính kèm, đa ngôn ngữ |

## 3. Dữ liệu

| Tập | Quy mô | Vai trò |
|---|---|---|
| Huấn luyện / phát triển | 80 ticket có nhãn | Thử prompt, không dùng để đánh giá |
| Kiểm định | 40 ticket có nhãn | Giữ kín tới Session 5. Mọi số liệu trong tài liệu này đo trên tập này |
| Kho tri thức | 28 tài liệu | Trong đó 2 tài liệu ở trạng thái đã bị thay thế |
| Hỏi–đáp vàng | 40 câu có đáp án + 5 câu không có | Đo truy hồi và tỉ lệ từ chối |
| Ca đối kháng | 12 ca | Kiểm thử guardrails |

**Toàn bộ là dữ liệu sinh tổng hợp.** Không có dữ liệu khách hàng thật ở bất kỳ khâu nào. Số thuê bao dùng dải `098700xxxx` không tồn tại thực tế.

**Hệ quả cần nói rõ:** dữ liệu sinh tổng hợp không phản ánh đầy đủ phân bố ticket thật. Độ chính xác đo trên tập này là **giới hạn trên**, không phải dự báo cho môi trường thật.

## 4. Kết quả đánh giá

Đo trên tập kiểm định 40 ticket, cấu hình *điền*. Chi tiết ở [`docs/EVALUATION.md`](../docs/EVALUATION.md).

| Nhóm | Chỉ số chính | Đo được |
|---|---|---|
| Phân loại | Accuracy / Macro-F1 | *điền* |
| Truy hồi | Recall@5 | *điền* |
| Sinh văn bản | Tỉ lệ trích dẫn hợp lệ | *điền* |
| Vận hành | p95 mỗi ticket | *điền* |
| An toàn | Chuyển người đúng / 12 ca đối kháng | *điền* |

## 5. Kiểm tra thiên lệch

Chạy `uv run python scripts/bias_check.py`. Câu hỏi: **hệ thống có xử lý khác nhau giữa các nhóm khách hàng không?**

| Chiều | Nhóm | Độ chính xác | Tỉ lệ chuyển người | Số ca |
|---|---|---|---|---|
| Văn phong | ngắn gọn | | | |
| | đầy đủ | | | |
| Sắc thái | trung_tinh | | | |
| | buc_boi | | | |
| | gay_gat | | | |
| Kênh | app | | | |
| | hotline | | | |
| | email | | | |

**Chênh lệch lớn nhất:** *điền*. Ngưỡng cảnh báo là 15 điểm phần trăm.

**Nếu có chênh lệch vượt ngưỡng, phải ghi vào mục 6 như một giới hạn**, không phải giấu đi.

**Giới hạn của chính phép kiểm tra này:** tập kiểm định chỉ 40 ticket, một số nhóm dưới 5 ca. Chênh lệch trên nhóm dưới 5 ca chưa đủ căn cứ kết luận.

## 6. Giới hạn đã biết

> **Tối thiểu ba giới hạn cụ thể, rút ra từ phân tích lỗi.** Không viết chung chung.

1. **Nhầm lẫn giữa `cuoc_thanh_toan` và `goi_cuoc_khuyen_mai`.** *Điền tỉ lệ đo được.* Nguyên nhân là hai nhóm chồng lấn về ngữ nghĩa: ticket nhắc tên gói nhưng vấn đề thực là tiền đã bị trừ. Đây là giới hạn ở **định nghĩa nhãn**, không phải ở model — sửa bằng cách sửa model sẽ không hiệu quả.

2. **Ngưỡng truy hồi 0.62 hiệu chuẩn bằng số đo cho hybrid `bge-m3`, không có căn cứ lý thuyết.** Phải hiệu chuẩn lại nếu đổi model embedding hoặc chiến lược chia đoạn. Ngưỡng đặt sai theo hướng thấp làm hệ thống bịa chính sách; đặt sai theo hướng cao làm tỉ lệ chuyển người tăng vô ích.

3. *Điền giới hạn thứ ba từ phân tích lỗi của nhóm.*

4. **Số liệu chỉ có giá trị trên cấu hình đã ghi.** Chuyển sang cấu hình còn lại thì toàn bộ bảng chỉ số phải đo lại. Không nội suy.

5. **Dữ liệu sinh tổng hợp.** Phân bố ticket thật có thể khác đáng kể, đặc biệt ở nhóm `khac` và ở các ca không lường trước.

## 7. Rủi ro đã lường trước và biện pháp

| Rủi ro | Mức | Biện pháp | Còn lại gì |
|---|---|---|---|
| Bịa ra chính sách không có trong kho | Cao nhất | Ngưỡng truy hồi + quy tắc từ chối + bắt buộc trích dẫn ([ADR-0005](../docs/adr/0005-nguong-tu-choi-thay-vi-doan.md)) | Ngưỡng sai hướng thấp vẫn để lọt |
| Cam kết bồi thường sai thành nghĩa vụ | Cao nhất | Guardrail đầu ra chặn cam kết tiền không có trong ngữ cảnh | Cách diễn đạt lạ có thể vượt bộ lọc |
| Trích dẫn chính sách hết hiệu lực | Cao | Lọc theo `status`, tài liệu bị thay thế không vào chỉ mục | Phụ thuộc việc front-matter được cập nhật đúng |
| Rò rỉ PII qua nhật ký | Cao | Che PII trước khi ghi log | Chỉ che các mẫu đã biết |
| Chèn lệnh qua nội dung ticket | Trung bình | Thẻ phân tách + phát hiện mẫu + đánh dấu chuyển người | Bộ mẫu hữu hạn, không đầy đủ |

## 8. Giám sát sau triển khai

| Tín hiệu | Ngưỡng cảnh báo | Nghĩa là gì |
|---|---|---|
| Tỉ lệ người duyệt phải sửa | Tăng > 10 điểm phần trăm trong 7 ngày | Phân bố ticket dịch chuyển, hoặc chính sách vừa cập nhật |
| Tỉ lệ từ chối | Tăng > 5 điểm phần trăm | Chất lượng dự thảo giảm |
| Tỉ lệ chuyển người vì không đủ căn cứ | Tăng đột biến | Kho tri thức thiếu tài liệu cho loại yêu cầu mới |
| p95 độ trễ | Vượt ngưỡng cam kết | Tải vượt năng lực, hoặc dịch vụ model suy giảm |

**Tỉ lệ sửa và tỉ lệ từ chối của người duyệt là tín hiệu phát hiện suy giảm sớm nhất mà hệ thống có** — sớm hơn điểm đánh giá tự động, vì nó phản ánh phán đoán của người thật trên ca thật.

## 9. Liên hệ và trách nhiệm

Xem `docs/handover/RESPONSIBILITIES.md`.
