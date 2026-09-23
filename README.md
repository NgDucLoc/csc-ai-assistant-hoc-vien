# csc-ai-assistant

**Trợ lý xử lý ticket Chăm sóc khách hàng viễn thông** — Development Starter Kit cho môn *AI-Native Application Engineering* (24 giờ · 3 ngày · 6 session).

Hệ thống hỗ trợ giao dịch viên phân loại ticket, tra cứu chính sách và soạn dự thảo phản hồi. **Không thay thế giao dịch viên:** không có đường dẫn nào cho phép phản hồi tới khách hàng mà chưa qua thao tác duyệt của con người.

---

## Bắt đầu

```bash
uv sync --all-extras
uv run pre-commit install
cp .env.example .env
uv run python scripts/check_env.py
```

Chi tiết ở [`SETUP.md`](SETUP.md) và [`labs/LAB-0.md`](labs/LAB-0.md).

## Chạy

```bash
uv run streamlit run src/ui/app.py                    # giao diện :8501
uv run uvicorn src.api.main:app --reload              # API :8000, tài liệu ở /docs
docker compose up --build                             # cả ba dịch vụ
```

## Cấu trúc

```
src/
  config.py            Nơi DUY NHẤT đọc biến môi trường
  llm/                 client · cache · schema (4 lớp phòng vệ đầu ra)
  knowledge/           loader · indexer · retriever
  agent/               prompts/ · classifier · tools · generator · workflow
  guardrails/          input_rules · output_rules · runtime (logging, trace)
  api/main.py          API bất đồng bộ + worker nền
  ui/app.py            Gửi ticket · Hàng đợi duyệt · Theo dõi
  store.py             Hàng đợi và nhật ký duyệt (SQLite ngoài tiến trình)
data/                  120 ticket · 28 tài liệu tri thức · gold QA · fixtures
eval/                  run_eval.py · metrics.py (5 nhóm chỉ số)
tests/                 test_lab1…5 + 12 ca đối kháng
scripts/               check_env · build_index · validate_data · rescue · grade …
labs/                  Đề bài LAB-0 … LAB-6 (giảng viên viết, cố định)
workbooks/             Chỗ học viên viết trong giờ — WORKBOOK-1 … 6
docs/                  canvas · blueprint · context_spec · EVALUATION · MODEL_CARD
  adr/                 Quyết định kiến trúc, mẫu bốn phần
  handover/            RUNBOOK · INCIDENTS · RESPONSIBILITIES
```

## Sáu buổi, một sản phẩm

Không phải sáu bài tập độc lập. Mỗi buổi bổ sung một tầng năng lực cho cùng một sản phẩm; deliverable của buổi trước là đầu vào bắt buộc của buổi sau.

| Buổi | Deliverable | Tầng được bổ sung |
|---|---|---|
| 1 | AI Opportunity Canvas | Phạm vi và ranh giới. Chưa viết code |
| 2 | AI Solution Blueprint | Kiến trúc. Khung chạy được |
| 3 | Context Specification | **Bộ não** — prompt, ngữ cảnh, tri thức, truy hồi |
| 4 | AI Prototype v1 | **Quy trình** — workflow, công cụ, human-in-the-loop |
| 5 | Production-ready Prototype | **Vỏ bọc** — API, Docker, đánh giá, guardrails, logging |
| 6 | Final AI Application | Cải tiến dựa trên số liệu, demo, phản biện |

## Hai cấu hình chạy

Cả hai là công dân hạng nhất. Chuyển đổi **chỉ bằng biến môi trường**, không sửa mã.

| | Cấu hình S | Cấu hình L |
|---|---|---|
| Máy chủ suy luận | vLLM trên GPU, gộp lô liên tục | Ollama trên máy học viên |
| Model sinh văn bản | `Qwen3-8B` | `qwen3:8b` — **cố ý cùng một model, khác backend** |
| Model embedding | `bge-m3` | `bge-m3` — **cố ý giống nhau** |
| Điểm mạnh | Chất lượng cao, phục vụ đồng thời tốt | Độc lập, không có điểm hỏng chung |

Model embedding giống nhau ở cả hai cấu hình là **ràng buộc bắt buộc**: nhờ đó chỉ mục dựng ở cấu hình nào cũng đọc được ở cấu hình kia, và quyết định hạ tầng không ảnh hưởng tới kho tri thức.

Cấu hình nào làm chuẩn của lớp được quyết bằng phép đo (`scripts/bench_server.py`) trước khóa một tuần, không quyết trước bằng phỏng đoán.

> **Hạ tầng phòng Lab đang dùng:** 8 AI Workstation độc lập, mỗi máy 1× RTX 5080 16GB — **1 nhóm 1 workstation**, không cluster hóa. Mặc định vẫn chạy cấu hình L (Ollama) trên chính GPU đó, không đổi mặc định lớp. Muốn thử triển khai vLLM thật tận dụng VRAM dư, xem `CHALLENGE.md` mục 5.4 (nội dung nâng cao, tùy chọn). Chi tiết quyết định ở `PROJECT-SPEC.md` Mục 17, mục v1.5.

## Kiểm thử và đánh giá

```bash
uv run pytest                                # toàn bộ
uv run pytest -m lab3                         # theo buổi
uv run python scripts/validate_data.py        # toàn vẹn dữ liệu và bẫy sư phạm
uv run python eval/run_eval.py --background   # 5 nhóm chỉ số, chạy nền
uv run python scripts/bias_check.py           # kiểm tra thiên lệch
```

**Bộ kiểm thử chạy được mà không cần máy chủ suy luận.** Đó là một tính chất của thiết kế, không phải may mắn: `.cache/llm_cache.db` được commit và `CACHE_MODE=cache_only` khiến kết quả gọi model trở nên tất định.

## Công cụ vận hành lớp học

Sáu session ghép thành ba ngày, mỗi ngày hai buổi. Giữa buổi sáng và buổi chiều **chỉ có giờ nghỉ trưa** — nhóm tụt lại không có đêm để bù.

```bash
uv run python scripts/checkpoint.py 3    # 5 phút cuối buổi: đủ điều kiện chưa?
./scripts/rescue.sh 3                     # cứu hộ dưới 2 phút, KHÔNG đụng docs/
./scripts/rescue.sh 3 --bundle /Volumes/USB/csc.bundle   # khi không có mạng
uv run python scripts/grade.py 3 --team nhom-a           # chấm phần định lượng
```

`rescue.sh` đồng bộ `src/`, `data/` và `.cache/` từ `solution/session-N`, **không đụng vào `docs/`** — canvas, blueprint và ADR là deliverable của nhóm.

## Tài liệu ràng buộc

Mọi quyết định kỹ thuật tra cứu `PROJECT-SPEC.md` trước. Mã spec (ví dụ `SPEC-RAG-03`) được trích dẫn trong mã nguồn, commit và báo lỗi để truy vết.

## Ba ranh giới không được vượt

1. **Không có đường dẫn nào tới khách hàng mà chưa qua người duyệt** (`SPEC-FLOW-03`). Ép bằng `test_no_path_reaches_customer_without_human_approval`.
2. **Không lời gọi model nào ngoài `src/llm/client.py`** (`SPEC-ARCH-02`). Ép bằng `test_no_llm_call_outside_client`.
3. **Toàn bộ dữ liệu là dữ liệu sinh tổng hợp** (`SPEC-DATA-01`). Ép bằng hook `pre-commit`.
