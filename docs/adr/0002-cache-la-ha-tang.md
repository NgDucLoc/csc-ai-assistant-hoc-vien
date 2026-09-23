# ADR-0002: Coi lớp cache là hạ tầng bắt buộc, và commit tệp cache vào repo

- **Trạng thái:** đã chấp thuận
- **Ngày:** 2026-01-16
- **Người quyết định:** Hội đồng xây dựng chương trình
- **Mã spec liên quan:** SPEC-LLM-02, SPEC-TOOLING-04, SPEC-INFRA-07

## Bối cảnh

Khóa học muốn dạy tích hợp liên tục có cổng chất lượng cho ứng dụng AI. Nhưng chạy đánh giá tự động cho ứng dụng AI thông thường rất tốn kém: mỗi lần chạy đều phải gọi model, nghĩa là runner CI phải có GPU hoặc phải gọi ra mạng ngoài. Cả hai đều không khả thi với điều kiện của lớp học.

Đồng thời, hệ thống cần một lớp dự phòng cuối cùng cho tình huống mất cả server lẫn Ollama giữa buổi.

## Các phương án đã cân nhắc

1. **Không cache, CI chỉ chạy lint và unit test.** Ưu: đơn giản. Nhược: bỏ mất nội dung giảng dạy quan trọng nhất về kỹ thuật phần mềm AI — chất lượng model được kiểm soát tự động giống như kiểm soát lỗi biên dịch. Học viên giữ nguyên thói quen sửa prompt rồi chạy tay xem có ổn không, đúng thói quen mà khóa học cần thay đổi.

2. **Cache trong bộ nhớ, sinh lại mỗi lần chạy.** Ưu: không phình repo. Nhược: không giúp gì cho CI, không giúp gì cho phương án dự phòng.

3. **Cache SQLite trên đĩa, tệp cache được commit vào repo.** Ưu: CI đọc lại kết quả đã lưu, chạy được trên runner không GPU không mạng; đồng thời là lớp dự phòng thứ ba; và làm kết quả đánh giá tái lập được. Nhược: tệp nhị phân trong repo, xung đột khi merge, và phải kỷ luật sinh lại cache mỗi khi prompt đổi.

## Quyết định

Chọn phương án 3. `.cache/llm_cache.db` **bắt buộc được commit**, và `.gitignore` có ghi chú rõ cấm thêm `.cache/` vào danh sách bỏ qua.

Khóa cache **bắt buộc bao gồm `base_url` và tên model**. Bỏ hai trường này thì kết quả sinh ở cấu hình S sẽ được dùng lại cho cấu hình L, và mọi so sánh giữa hai cấu hình trở thành vô nghĩa mà không ai phát hiện ra.

Ba chế độ: `on` (đọc trước, gọi khi trượt), `cache_only` (cấm gọi model, trượt là lỗi chặn), `off` (luôn gọi thật, dùng khi đo độ trễ).

## Hệ quả chấp nhận

- **Mọi PR sửa prompt bắt buộc kèm cache sinh lại trong cùng PR.** Không có luật này, CI đỏ hàng loạt và cả đội học cách phớt lờ nó — mà một cổng chất lượng bị phớt lờ còn tệ hơn không có cổng.
- Repo phình thêm vài chục MB. Chấp nhận, và `check-added-large-files` được nới lên 6 MB riêng cho tệp này.
- Xung đột merge trên tệp nhị phân không giải được bằng tay. Quy ước: lấy bản của nhánh đích rồi chạy lại `scripts/warm_cache.py`.
- Đo độ trễ thật bắt buộc đặt `CACHE_MODE=off`. `scripts/bench_server.py` cảnh báo khi phát hiện chế độ khác — nếu không, học viên sẽ vô tình đo tốc độ đọc SQLite và báo cáo con số đẹp vô nghĩa.
