# ADR-0004: Đặt dịch vụ model bên ngoài container ứng dụng

- **Trạng thái:** đã chấp thuận
- **Ngày:** 2026-01-18
- **Người quyết định:** Hội đồng xây dựng chương trình
- **Mã spec liên quan:** [SPEC-ARCH-02](../../PROJECT-SPEC.md#spec-arch-02), [SPEC-INFRA-01](../../PROJECT-SPEC.md#spec-infra-01)

## Bối cảnh

Session 5 yêu cầu đóng gói ứng dụng bằng Docker sao cho khởi động lại được trên máy sạch bằng một lệnh. Câu hỏi đặt ra: model ngôn ngữ có nằm trong gói đó không?

Ràng buộc thực tế: máy học viên tối thiểu 8 GB RAM, 10 GB đĩa trống, không card đồ họa. Model `qwen2.5:3b` khoảng 2 GB, `bge-m3` khoảng 1,2 GB.

## Các phương án đã cân nhắc

1. **Nhét model vào ảnh ứng dụng.** Ưu: một lệnh duy nhất thật sự, không phụ thuộc gì bên ngoài. Nhược: ảnh phình lên vài GB; mỗi lần sửa một dòng Python phải dựng lại cả khối; và mất luôn khả năng chuyển giữa cấu hình S và L, vì cấu hình S vốn dùng server ở ngoài.

2. **Chạy Ollama như một dịch vụ trong `docker-compose`.** Ưu: vẫn là một lệnh; model tách khỏi ảnh ứng dụng. Nhược: Docker Desktop trên macOS và Windows chạy trong máy ảo, nên Ollama trong container mất khả năng dùng tăng tốc phần cứng của máy chủ, chậm hơn đáng kể so với chạy trực tiếp. Học viên đã cài Ollama ở Lab 0 rồi, chạy thêm một bản trong container là tải model lần thứ hai — mà ngân sách đĩa chỉ có 10 GB.

3. **Model nằm ngoài container, truy cập qua `host.docker.internal`.** Ưu: ảnh ứng dụng nhẹ và dựng nhanh; chuyển S↔L chỉ là đổi `LLM_BASE_URL`, không dựng lại ảnh; không tải model lần hai. Nhược: "một lệnh khởi động" có kèm điều kiện — máy phải có sẵn dịch vụ model.

## Quyết định

Chọn phương án 3. [`docker-compose.yml`](../../docker-compose.yml) gồm ba dịch vụ ứng dụng (api, ui, mlflow); dịch vụ model nằm ngoài, địa chỉ truyền qua biến môi trường.

Tiêu chí quyết định: **thành phần nặng nhất, thay đổi ít nhất, và cần cấu hình phần cứng riêng thì tách ra.** Đây cũng chính là nguyên tắc tách tầng API khỏi tầng model để hai tầng mở rộng độc lập — nội dung được giảng ở Session 5.

## Hệ quả chấp nhận

- Tiêu chí "khởi động từ máy sạch bằng một lệnh" phải phát biểu chính xác hơn: máy sạch **đã hoàn thành Lab 0**. [`SETUP.md`](../../SETUP.md) nêu rõ điều kiện này.
- `extra_hosts: host.docker.internal:host-gateway` bắt buộc có mặt, nếu không container trên Linux không thấy được dịch vụ trên máy chủ.
- Khi chấm Lab 5, nếu Docker lỗi trên máy Windows của học viên, phần đóng gói được chấm qua tệp cấu hình đã viết chứ không qua việc chạy được — vì nút thắt nằm ở Docker Desktop, không nằm ở thiết kế của nhóm.
