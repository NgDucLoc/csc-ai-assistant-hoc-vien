# LAB 0 — Chuẩn bị môi trường

**Hình thức:** tự thực hiện tại nhà. Không có giảng viên bên cạnh, nên mọi lỗi trong bài này đều kèm hướng dẫn khắc phục ngay trong kết quả chạy.

**Chia hai phần, hai hạn nộp khác nhau:**

| Phần | Nội dung | Thời lượng | Hạn |
|---|---|---|---|
| A | Cấu hình chuẩn của lớp | ~20 phút | Trước ngày học đầu tiên 48 giờ |
| B | Cấu hình còn lại | ~40 phút | Trước Session 5 |

> Đơn vị tổ chức thông báo cấu hình nào là chuẩn khi gửi hướng dẫn này.

Nếu để việc cài đặt diễn ra trong giờ học, buổi sáng ngày đầu tiên mất gần như hoàn toàn — và trong khóa ba ngày, đó là mất một phần sáu chương trình.

---

## Phần A — Cấu hình chuẩn của lớp

### A1. Cài công cụ nền

| Công cụ | Kiểm tra |
|---|---|
| Python 3.11 | `python --version` |
| Git | `git --version` |
| Docker Desktop | `docker --version` |
| uv | `uv --version` |

Cài `uv`:
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### A2. Dựng môi trường

```bash
git clone <repo> && cd csc-ai-assistant
uv sync --all-extras
uv run pre-commit install
cp .env.example .env
```

`uv sync` đọc [`uv.lock`](../uv.lock) — tệp khóa phiên bản được commit vào repo. Nhờ nó mọi máy học viên có đúng cùng bộ thư viện, và lỗi "máy tôi chạy được" không xảy ra.

`pre-commit install` gắn hook chặn commit chứa dữ liệu nhạy cảm. Không phải thủ tục hình thức: khóa truy cập server dùng chung bị lộ nghĩa là phải cấp lại cho cả lớp giữa buổi.

### A3. Kết nối máy chủ suy luận

**Nếu lớp dùng cấu hình S** — sửa `.env`:
```
CONFIG_PROFILE=S
LLM_BASE_URL=http://<địa chỉ server>/v1
LLM_MODEL=Qwen3-8B
LLM_API_KEY=<khóa giảng viên cấp>
EMBED_BASE_URL=http://<địa chỉ server>/v1
EMBED_MODEL=bge-m3
```

**Nếu lớp dùng cấu hình L** — cài Ollama rồi tải hai model:
```bash
ollama serve
ollama pull qwen3:8b               # ~5,0 GB
ollama pull bge-m3                # ~1,2 GB
```
Giữ nguyên `.env` mặc định.

### A4. Chạy kiểm tra

```bash
uv run python scripts/check_env.py
```

Toàn bộ hạng mục phải báo `PASS`. Mỗi hạng mục `FAIL` có hướng dẫn khắc phục in ngay bên dưới — đọc và làm theo trước khi hỏi.

### A5. Nộp

Chụp màn hình kết quả `check_env.py` và nộp theo hướng dẫn của giảng viên.

---

## Phần B — Cấu hình còn lại

**Trước Session 5.** Phần này trông thừa khi cấu hình chuẩn hoạt động bình thường, nhưng không được bỏ, vì hai lý do:

1. Nếu lớp dùng server dùng chung thì **server sập đồng nghĩa cả lớp dừng** — khác hẳn tình huống mỗi máy chạy độc lập. Với nhịp ba ngày, mất nửa buổi không có cách nào bù.
2. Bước kiểm thử tải ở Session 5 **bắt buộc đo trên cả hai cấu hình** để có cơ sở so sánh.

### B1. Chuẩn bị cấu hình còn lại

Làm phần A3 cho cấu hình chưa cài.

### B2. Kiểm tra

```bash
uv run python scripts/check_env.py --profile S
uv run python scripts/check_env.py --profile L
```

Cả hai phải `PASS`.

---

## Điều kiện hoàn thành

- [ ] `uv sync` chạy xong, thư mục `.venv` tồn tại
- [ ] `pre-commit` đã gắn vào Git
- [ ] `.env` đã tạo từ [`.env.example`](../.env.example)
- [ ] `check_env.py` báo PASS toàn bộ ở cấu hình chuẩn
- [ ] Đã nộp ảnh chụp màn hình
- [ ] (Trước Session 5) `check_env.py` PASS ở cả hai cấu hình

Tự kiểm tra: `uv run python scripts/checkpoint.py 0`

---

## Yêu cầu về máy

| Hạng mục | Tối thiểu | Khuyến nghị |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Đĩa trống | 10 GB | 15 GB |
| CPU | 4 nhân | 8 nhân |
| GPU | Không yêu cầu | Không yêu cầu |
| Hệ điều hành | Windows 10+, macOS 12+, Ubuntu 20.04+ | |

**Về 10 GB đĩa trống:** máy không được reset giữa ba ngày học. Tới chiều ngày 3 nó chứa model đã tải, ảnh Docker, chỉ mục, `mlruns/` và cache. `check_env.py` kiểm tra ngân sách này — nếu báo FAIL, dọn bớt trước khi vào lớp chứ đừng bỏ qua.
