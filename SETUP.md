# SETUP

Hướng dẫn dựng môi trường. Làm tại nhà trước ngày học đầu tiên — nếu để việc cài đặt diễn ra trong giờ học, buổi sáng ngày đầu tiên mất gần như hoàn toàn.

Đề bài đầy đủ ở [`labs/LAB-0.md`](labs/LAB-0.md).

---

## Yêu cầu về máy

| Hạng mục | Tối thiểu | Khuyến nghị |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Đĩa trống | 10 GB | 15 GB |
| CPU | 4 nhân | 8 nhân |
| GPU | Không yêu cầu | Không yêu cầu |
| Hệ điều hành | Windows 10+ · macOS 12+ · Ubuntu 20.04+ | |

**Về 10 GB đĩa trống:** máy không được reset giữa ba ngày học. Tới chiều ngày 3 nó chứa model đã tải (~3,2 GB), ảnh Docker, chỉ mục, `mlruns/` và cache.

## 1. Công cụ nền

```bash
# uv — quản lý môi trường và khóa phiên bản
curl -LsSf https://astral.sh/uv/install.sh | sh          # macOS / Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

Cần thêm: Python 3.11, Git, Docker Desktop.

## 2. Dựng môi trường

```bash
git clone <repo> && cd csc-ai-assistant
uv sync --all-extras
uv run pre-commit install
cp .env.example .env
```

`uv sync` đọc [`uv.lock`](uv.lock) được commit trong repo, nên mọi máy có đúng cùng bộ thư viện.

## 3. Chọn cấu hình

### Cấu hình L — chạy cục bộ (mặc định)

```bash
ollama serve
ollama pull qwen3:8b                # ~5,0 GB
ollama pull bge-m3                 # ~1,2 GB
```

`.env` giữ nguyên mặc định.

### Cấu hình S — server dùng chung

Sửa `.env`:

```
CONFIG_PROFILE=S
LLM_BASE_URL=http://<server>/v1
LLM_MODEL=Qwen3-8B
LLM_API_KEY=<khóa giảng viên cấp>
EMBED_BASE_URL=http://<server>/v1
EMBED_MODEL=bge-m3
```

> `EMBED_MODEL` phải là `bge-m3` ở **cả hai** cấu hình. Dùng model embedding khác gây lệch số chiều vector giữa các buổi và mất rất nhiều thời gian truy nguyên.

## 4. Kiểm tra

```bash
uv run python scripts/check_env.py
```

Mọi hạng mục phải `PASS`. Hạng mục `FAIL` có hướng dẫn khắc phục in ngay bên dưới.

Trước Session 5, kiểm cả hai cấu hình:

```bash
uv run python scripts/check_env.py --profile S
uv run python scripts/check_env.py --profile L
```

## 5. Chạy thử

```bash
uv run pytest -m lab1                       # không cần máy chủ suy luận
uv run streamlit run src/ui/app.py          # giao diện
```

---

## Ba lớp dự phòng

Chuyển đổi giữa ba lớp **chỉ bằng biến môi trường**, không sửa mã. Đây là yêu cầu thiết kế bắt buộc: nếu phải sửa mã mới chuyển được, đường dự phòng sẽ không bao giờ được kiểm thử và sẽ hỏng đúng lúc cần dùng.

| Lớp | Cách bật | Dùng khi |
|---|---|---|
| 1 | `CONFIG_PROFILE=<chuẩn của lớp>` | Mặc định mọi buổi học |
| 2 | Đổi `CONFIG_PROFILE` sang cấu hình còn lại | Cấu hình chuẩn gặp sự cố; đo tải ở Session 5 |
| 3 | `CACHE_MODE=cache_only` | Mất cả hai đường trên, hoặc khi trình diễn |

## Khắc phục sự cố

| Triệu chứng | Xử lý |
|---|---|
| `uv sync` lỗi phiên bản Python | `uv python install 3.11` rồi chạy lại |
| `check_env` báo không kết nối được model | Cấu hình L: `ollama serve` đang chạy chưa? · Cấu hình S: kiểm tra `LLM_API_KEY` và mạng |
| `FileNotFoundError` khi truy hồi | Dùng bản dựng sẵn: [`data/index_prebuilt/`](data/index_prebuilt/), hoặc `uv run python scripts/build_index.py` |
| Docker lỗi trên Windows | Chạy trực tiếp các dịch vụ. Phần đóng gói được chấm qua tệp cấu hình |
| pre-commit chặn commit | Đọc thông báo — thường là số điện thoại thật hoặc khóa truy cập lọt vào repo |
| Đĩa đầy giữa khóa | `docker system prune`, xóa `eval/mlruns/` cũ |
