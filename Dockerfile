# Đóng gói ứng dụng — Session 5.
#
# Dịch vụ model KHÔNG nằm trong ảnh này. Lý do: model là thứ nặng nhất, thay
# đổi ít nhất, và cần cấu hình phần cứng riêng. Nhét nó vào ảnh ứng dụng làm
# mỗi lần sửa một dòng Python phải dựng lại vài GB, và làm mất luôn khả năng
# chuyển giữa cấu hình S và L bằng biến môi trường.

FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Khóa phụ thuộc trước, mã nguồn sau: đổi mã nguồn không phải cài lại thư viện.
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY src/ ./src/
COPY eval/ ./eval/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY .cache/ ./.cache/

RUN useradd --create-home --uid 10001 app \
 && mkdir -p /app/logs /app/data/index \
 && chown -R app:app /app
USER app

EXPOSE 8000 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
