# SỔ TAY VẬN HÀNH

> Bàn giao thiếu sổ tay vận hành là nguyên nhân phổ biến nhất khiến sản phẩm chết sau nghiệm thu. Tài liệu này viết cho người **chưa từng tham gia phát triển**.

## 1. Dựng lại hệ thống từ máy sạch

Điều kiện: máy đã cài Docker, Git, và có dịch vụ model chạy được (xem mục 2).

```bash
git clone <repo> && cd csc-ai-assistant
cp .env.example .env          # sửa CONFIG_PROFILE và LLM_BASE_URL
docker compose up --build     # api :8000 · ui :8501 · mlflow :5000
```

Kiểm chứng đã lên: `curl -s localhost:8000/health | jq`

Mốc thời gian mong đợi: dựng ảnh 3–5 phút lần đầu, khởi động 20 giây.

## 2. Dịch vụ model

Model **không** nằm trong container (ADR-0004). Hai lựa chọn:

**Cấu hình L — Ollama trên chính máy chủ:**
```bash
ollama serve
ollama pull qwen3:8b
ollama pull bge-m3
# .env: LLM_BASE_URL=http://host.docker.internal:11434/v1
```

**Cấu hình S — server GPU dùng chung:**
```bash
# .env: LLM_BASE_URL=http://<server>:4000/v1 và LLM_API_KEY=<khóa>
```

Chuyển giữa hai cấu hình **chỉ bằng biến môi trường**, không sửa mã, không dựng lại ảnh.

## 3. Thao tác hàng ngày

| Việc | Lệnh |
|---|---|
| Xem sức khỏe | `curl localhost:8000/health` |
| Xem chỉ số vận hành | `curl localhost:8000/metrics` |
| Xem hàng đợi chờ duyệt | `curl localhost:8000/review/queue` |
| Truy vết một ticket | `curl localhost:8000/trace/<trace_id>` |
| Xem nhật ký | `docker compose logs -f api` |
| Khởi động lại | `docker compose restart api` |

## 4. Cập nhật kho tri thức khi chính sách thay đổi

**Quy trình bắt buộc, không được rút gọn:**

1. Thêm tài liệu mới vào `data/knowledge/KB-NNN.md` với front-matter đầy đủ.
2. Nếu thay thế tài liệu cũ: đặt `supersedes: KB-XXX` ở bản mới, và đổi `status: superseded` ở bản cũ. **Không xóa bản cũ** — vụ việc phát sinh trước ngày hiệu lực mới vẫn cần tham chiếu nó.
3. Dựng lại chỉ mục: `uv run python scripts/build_index.py`
4. Chạy `uv run python scripts/validate_data.py`
5. Khởi động lại: `docker compose restart api ui`

> **Bỏ bước 3 là lỗi im lặng nguy hiểm nhất trong vận hành hệ thống này.** Chỉ mục lệch với kho tri thức không báo lỗi: truy hồi vẫn trả về kết quả, chỉ là kết quả của tài liệu cũ.

## 5. Chạy đánh giá định kỳ

Khuyến nghị hàng tháng, hoặc ngay sau mỗi lần cập nhật kho tri thức:

```bash
uv run python eval/run_eval.py --background
# theo dõi: cat eval/results/progress.json
```

So sánh với lần chạy trước trên MLflow tại `localhost:5000`. Chỉ số tụt quá 5 điểm phần trăm so với lần trước là dấu hiệu cần điều tra.

**Mọi bảng số liệu phải ghi kèm cấu hình.** Số đo trên hai cấu hình khác nhau không so sánh trực tiếp được.

## 6. Sao lưu

| Dữ liệu | Vị trí | Tần suất | Mất thì sao |
|---|---|---|---|
| Hàng đợi và nhật ký duyệt | volume `state` → `/app/state/app.db` | Hàng ngày | Mất tín hiệu chất lượng, mất ticket đang chờ |
| Nhật ký truy vết | volume `logs` → `/app/logs/app.jsonl` | Hàng ngày | Mất khả năng truy vết vụ việc cũ |
| Lần chạy đánh giá | volume `mlruns` | Hàng tuần | Mất bản đối chứng cho cải tiến |
| Chỉ mục tri thức | `data/index_prebuilt/` trong Git | Theo commit | Dựng lại được trong 4 phút |
| Cache model | `.cache/llm_cache.db` trong Git | Theo commit | CI mất khả năng chạy offline |

## 7. Ngân sách tài nguyên

| Hạng mục | Mức bình thường | Cần chú ý khi |
|---|---|---|
| RAM (3 dịch vụ) | ~1,5 GB | Vượt 3 GB |
| Đĩa (không kể model) | ~2 GB, tăng theo nhật ký | Vượt 8 GB — xoay vòng nhật ký |
| Model (ngoài container) | ~3,2 GB | |
| Số luồng worker | `API_WORKERS=2` | Tăng không giúp nếu nút thắt ở dịch vụ model |

**Nút thắt của toàn hệ thống là dịch vụ model, không phải tầng API.** Tăng `API_WORKERS` khi model đã bão hòa chỉ làm hàng đợi dài thêm chứ không tăng thông lượng.
