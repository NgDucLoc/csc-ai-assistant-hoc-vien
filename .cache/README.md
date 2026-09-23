# Lớp cache — hạ tầng, không phải tối ưu tốc độ

Thư mục này chứa `llm_cache.db`, và tệp đó **BẮT BUỘC được commit vào repo** (`SPEC-LLM-02`, ADR-0002).

Tệp README này tồn tại vì một lý do rất cụ thể: Git không theo dõi thư mục rỗng, nên khi `llm_cache.db` chưa được sinh, thư mục `.cache/` biến mất khỏi bản checkout và `COPY .cache/` trong Dockerfile hỏng ở giai đoạn 4 của CI. Giữ tệp này lại thì thư mục luôn tồn tại.

## Ba thứ treo vào tệp cache

1. **CI chạy được offline.** Runner không có GPU, không cài Ollama, không kết nối được server dùng chung. Nó đọc lại kết quả đã lưu. Không có cache thì cổng chất lượng tự động ở Lab 5 là bất khả thi.
2. **Lớp dự phòng thứ ba.** Mất cả server lẫn Ollama giữa buổi thì `CACHE_MODE=cache_only` vẫn cho lớp học tiếp tục.
3. **Kết quả đánh giá tái lập được.** Cùng đầu vào luôn cho cùng đầu ra.

## Sinh cache

Trên máy **có** máy chủ suy luận:

```bash
uv run python scripts/warm_cache.py
CACHE_MODE=cache_only uv run pytest -q      # kiểm chứng chạy được offline
git add .cache/llm_cache.db
git commit -m "[SPEC-LLM-02] Sinh lại cache"
```

## Luật bắt buộc sau khi đóng băng cache

**Mọi PR sửa prompt phải kèm cache sinh lại trong cùng PR.**

Không có luật này, CI đỏ hàng loạt và cả đội học cách phớt lờ nó — mà một cổng chất lượng bị phớt lờ còn tệ hơn không có cổng.

## Khóa cache

Khóa **bao gồm `base_url` và tên model**. Bỏ hai trường đó thì kết quả sinh ở cấu hình S sẽ được dùng lại cho cấu hình L, và mọi so sánh giữa hai cấu hình trở thành vô nghĩa mà không ai phát hiện ra.
