#!/usr/bin/env bash
# Chạy vLLM thật trên GPU của một workstation — nội dung nâng cao Session 5.
#
# Ollama (mặc định của cấu hình L) đã dùng GPU rời của workstation từ sau
# quyết định hạ tầng v1.5; vLLM ở đây không phải "thêm GPU" mà là đổi backend
# suy luận để so tốc độ thô, vẫn cùng một GPU. Vẫn giữ nguyên kiến trúc "một
# máy, một nhóm, không tranh giành" của cấu hình L (ADR-0001).
#
# Đây KHÔNG phải cấu hình mặc định của lớp. Xem CHALLENGE.md mục 5.4 và
# PROJECT-SPEC.md Mục 17 cho lý do.
#
# Dùng:
#   python3 -m venv .venv-vllm && source .venv-vllm/bin/activate && pip install vllm
#   ./scripts/run_vllm_local.sh [model] [port]
#
#   model  mặc định Qwen/Qwen3-8B-AWQ — bản lượng tử 4-bit, ước lượng ~5-6 GB
#          VRAM (CHƯA kiểm chứng repo này tồn tại trên HuggingFace — kiểm tra
#          trước buổi học; nếu không có bản AWQ chính thức, dùng Qwen/Qwen3-8B
#          gốc với --dtype bfloat16 hoặc bản GPTQ/GGUF tương đương).
#          An toàn cho GPU 16 GB: còn dư chỗ cho bge-m3 và KV cache.
#   port   mặc định 8001 (8000 đã dùng cho API của ứng dụng — src/api/main.py)

set -euo pipefail

MODEL="${1:-Qwen/Qwen3-8B-AWQ}"
PORT="${2:-8001}"

command -v vllm >/dev/null || {
  echo "Chưa cài vllm. Cài trong MÔI TRƯỜNG RIÊNG, không chung với 'uv sync' của repo" >&2
  echo "(vllm kéo theo torch/CUDA nặng, không nên trộn vào phụ thuộc của ứng dụng):" >&2
  echo "    python3 -m venv .venv-vllm && source .venv-vllm/bin/activate && pip install vllm" >&2
  exit 1
}

echo "═══ Khởi động vLLM ═══"
echo "  model : ${MODEL}"
echo "  cổng  : ${PORT}"
echo
echo "Sau khi thấy 'Uvicorn running', sửa .env của nhóm:"
echo "    LLM_BASE_URL=http://localhost:${PORT}/v1"
echo "    LLM_MODEL=${MODEL}"
echo
echo "Rồi đo và so sánh với đường nền Ollama:"
echo "    CACHE_MODE=off uv run python scripts/bench_server.py --out eval/results/bench-vllm-gpu.json"
echo "    nvidia-smi   # xem VRAM thực dùng, điền vào bảng ở CHALLENGE.md mục 5.4"
echo

# --reasoning-parser: BẮT BUỘC cho Qwen3 — đã kiểm chứng (2026-09-23) rằng
# Ollama tự tách khối <think> ra field riêng, KHÔNG để lọt vào content, nhưng
# vLLM không làm việc này tự động. Thiếu cờ này, <think>...</think> lọt thẳng
# vào message.content và phá lớp kiểm định JSON ở src/llm/schema.py — mọi
# ticket sẽ rơi vào fallback needs_human dù model trả lời đúng bên trong.
#
# --gpu-memory-utilization 0.70: chừa chỗ cho hệ điều hành và driver trên card
# 16 GB, không chiếm hết để vLLM không OOM khi context dài hơn dự kiến.
exec vllm serve "${MODEL}" \
  --port "${PORT}" \
  --gpu-memory-utilization 0.70 \
  --max-model-len 4096 \
  --dtype auto \
  --reasoning-parser qwen3
