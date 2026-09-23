# ADR-0001: Duy trì hai cấu hình chạy ngang hàng thay vì chọn cứng một cấu hình

- **Trạng thái:** đã chấp thuận
- **Ngày:** 2026-01-15
- **Người quyết định:** Hội đồng xây dựng chương trình
- **Mã spec liên quan:** SPEC-INFRA-01, SPEC-INFRA-02, SPEC-INFRA-07

## Bối cảnh

Khóa học 24 giờ diễn ra trong ba ngày liên tiếp, sáu buổi, tại một phòng học cố định. Hạ tầng suy luận có hai lựa chọn: một server GPU dùng chung, hoặc Ollama chạy trên laptop từng học viên.

Chưa biết trước năng lực server tại thời điểm thiết kế. Điều đã biết chắc là: nếu cấu hình chuẩn hỏng giữa buổi mà không có đường lùi, cả lớp dừng, và mất một buổi trong ba ngày là mất một phần sáu khóa học.

## Các phương án đã cân nhắc

1. **Chỉ dùng server GPU.** Ưu: chất lượng đầu ra cao hơn hẳn với model 7B; phục vụ đồng thời tốt nhờ gộp lô liên tục. Nhược: điểm hỏng đơn — server sập hoặc đường truyền chập chờn là cả lớp dừng. Với nhịp ba ngày không có đêm để bù, thiệt hại này không thể chấp nhận.

2. **Chỉ dùng Ollama cục bộ.** Ưu: mỗi máy độc lập, không có điểm hỏng chung. Nhược: model 3B cho chất lượng thấp hơn rõ rệt; sản phẩm demo cuối khóa kém thuyết phục; không dạy được nội dung về gộp lô liên tục và bài toán đồng thời ở Session 5.

3. **Hai cấu hình ngang hàng, cùng một đường code, chuyển bằng biến môi trường.** Ưu: có đường lùi thật; dạy được cả hai mặt của bài toán hạ tầng; Session 5 so sánh được năng lực phục vụ giữa hai kiến trúc suy luận. Nhược: phải kiểm thử cả hai đường trong CI, và phải giữ kỷ luật không để một đường phình ra so với đường kia.

## Quyết định

Chọn phương án 3. Cả hai cấu hình là **công dân hạng nhất**: cùng một đường code, chuyển đổi chỉ bằng `CONFIG_PROFILE`, `LLM_BASE_URL` và `LLM_MODEL`, cùng được kiểm thử trong CI.

Tiêu chí quyết định: **đường lùi không được kiểm thử là đường lùi hỏng.** Một phương án dự phòng chỉ tồn tại trên giấy sẽ hỏng đúng lúc cần dùng. Cách duy nhất giữ nó sống là để nó là một lựa chọn chính thức, không phải một nhánh phụ.

Cấu hình nào làm chuẩn của lớp được quyết bằng phép đo (`scripts/bench_server.py`) trước khóa một tuần, không quyết trước bằng phỏng đoán.

## Hệ quả chấp nhận

- `LLMClient` bị ràng buộc phải phơi cùng một giao diện cho cả hai đầu. Điều này khả thi vì cả vLLM lẫn Ollama đều có API tương thích OpenAI — nếu một trong hai không có, quyết định này phải xem xét lại.
- **Model embedding bắt buộc giống nhau ở cả hai cấu hình** (`bge-m3`). Đây là hệ quả ràng buộc nhất: nó tách bạch quyết định hạ tầng khỏi kho tri thức, và đổi lại là không được chọn model embedding tối ưu riêng cho từng đầu.
- Mọi số liệu bắt buộc ghi kèm `config_profile`. Bảng số liệu thiếu cột cấu hình không được chấp nhận, vì hai cấu hình cho hai dải kết quả khác nhau.
- CI phải chạy ma trận hai cấu hình, làm thời gian CI dài gấp đôi. Chấp nhận vì đây là cái giá của việc đường lùi thực sự hoạt động.
