"""Cấu hình tập trung cho toàn hệ thống.

Đây là nơi DUY NHẤT đọc biến môi trường. Mọi module khác import ``settings``
từ đây thay vì gọi ``os.getenv``. Nhờ vậy việc chuyển giữa cấu hình S và cấu
hình L (SPEC-INFRA-01) thực sự chỉ là đổi biến môi trường, và bài kiểm thử có
thể ép một cấu hình cụ thể mà không phải vá từng chỗ.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parent.parent

ConfigProfile = Literal["S", "L"]
CacheMode = Literal["on", "cache_only", "off"]


def _load_dotenv(path: Path) -> None:
    """Nạp tệp .env vào os.environ mà không ghi đè biến đã có sẵn.

    Tự cài đặt thay vì phụ thuộc python-dotenv để ``scripts/check_env.py``
    chạy được ngay cả khi môi trường chưa dựng xong — đó chính là lúc học
    viên cần nó nhất.
    """
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv(ROOT / ".env")


def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Toàn bộ tham số vận hành của hệ thống, đọc một lần lúc khởi động."""

    # --- Hạ tầng: SPEC-INFRA-01 --------------------------------------------
    config_profile: ConfigProfile = field(default_factory=lambda: _env("CONFIG_PROFILE", "L"))
    llm_base_url: str = field(default_factory=lambda: _env("LLM_BASE_URL", "http://localhost:11434/v1"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "qwen3:8b"))
    llm_api_key: str = field(default_factory=lambda: _env("LLM_API_KEY", "ollama"))
    embed_base_url: str = field(default_factory=lambda: _env("EMBED_BASE_URL", "http://localhost:11434/v1"))
    embed_model: str = field(default_factory=lambda: _env("EMBED_MODEL", "bge-m3"))
    llm_timeout: int = field(default_factory=lambda: _env_int("LLM_TIMEOUT_SECONDS", 120))

    # --- Cache: SPEC-LLM-02 ------------------------------------------------
    cache_mode: CacheMode = field(default_factory=lambda: _env("CACHE_MODE", "on"))
    cache_path: str = field(default_factory=lambda: _env("CACHE_PATH", ".cache/llm_cache.db"))

    # --- Ngân sách tính toán: SPEC-INFRA-04 --------------------------------
    max_llm_calls_per_ticket: int = field(default_factory=lambda: _env_int("MAX_LLM_CALLS_PER_TICKET", 5))
    max_tool_calls_per_ticket: int = field(default_factory=lambda: _env_int("MAX_TOOL_CALLS_PER_TICKET", 3))
    max_system_prompt_tokens: int = field(default_factory=lambda: _env_int("MAX_SYSTEM_PROMPT_TOKENS", 800))
    max_context_tokens: int = field(default_factory=lambda: _env_int("MAX_CONTEXT_TOKENS", 3000))

    # --- Truy hồi: SPEC-RAG-01, SPEC-RAG-02 --------------------------------
    chunk_size: int = field(default_factory=lambda: _env_int("CHUNK_SIZE", 700))
    chunk_overlap: int = field(default_factory=lambda: _env_int("CHUNK_OVERLAP", 100))
    retrieve_top_k: int = field(default_factory=lambda: _env_int("RETRIEVE_TOP_K", 5))
    retrieve_min_score: float = field(default_factory=lambda: _env_float("RETRIEVE_MIN_SCORE", 0.62))
    retrieve_mode: str = field(default_factory=lambda: _env("RETRIEVE_MODE", "auto"))  # auto | keyword
    vector_weight: float = field(default_factory=lambda: _env_float("RETRIEVE_VECTOR_WEIGHT", 0.75))
    rerank_enabled: bool = field(
        default_factory=lambda: _env("RERANK_ENABLED", "false").lower() in ("1", "true", "yes", "on")
    )
    embed_batch_size: int = field(default_factory=lambda: _env_int("EMBED_BATCH_SIZE", 16))
    chroma_path: str = field(default_factory=lambda: _env("CHROMA_PATH", "data/index"))

    # --- Vận hành ----------------------------------------------------------
    db_path: str = field(default_factory=lambda: _env("DB_PATH", "data/app.db"))
    log_path: str = field(default_factory=lambda: _env("LOG_PATH", "logs/app.jsonl"))
    api_workers: int = field(default_factory=lambda: _env_int("API_WORKERS", 2))
    tool_timeout: int = field(default_factory=lambda: _env_int("TOOL_TIMEOUT_SECONDS", 5))
    breaker_threshold: int = field(default_factory=lambda: _env_int("CIRCUIT_BREAKER_THRESHOLD", 3))
    breaker_cooldown: int = field(default_factory=lambda: _env_int("CIRCUIT_BREAKER_COOLDOWN", 60))

    def abs_path(self, relative: str) -> Path:
        """Đổi một đường dẫn tương đối trong cấu hình thành đường dẫn tuyệt đối."""
        p = Path(relative)
        return p if p.is_absolute() else ROOT / p

    def profile_banner(self) -> str:
        """Chuỗi một dòng mô tả cấu hình đang chạy.

        SPEC-INFRA-03 buộc giao diện hiện rõ đang chạy ở cấu hình nào, vì một
        con số không kèm cấu hình sinh ra nó là một con số vô nghĩa.
        """
        return (
            f"Cấu hình {self.config_profile} · {self.llm_model} "
            f"@ {self.llm_base_url} · cache={self.cache_mode}"
        )


settings = Settings()

# Bảng tham số theo tác vụ — SPEC-LLM-03.
# Kết luận rút ra từ thí nghiệm ở Session 2 bước 2: một ứng dụng AI không dùng
# chung một cấu hình model cho mọi bước. Phân loại cần tất định; soạn phản hồi
# cần đủ độ linh hoạt để câu văn không cứng.
#
# ``reasoning_effort: "none"`` tắt chế độ suy luận (thinking) của Qwen3. Nếu bật, model
# dành hết ``max_tokens`` để "nghĩ" và trả về nội dung rỗng (đo được: phân loại một ticket
# với max_tokens=400 dừng ở giới hạn độ dài và ``content`` rỗng). Tham số này nằm trong khóa
# cache vì nó làm đổi đầu ra.
TASK_PARAMS: dict[str, dict[str, float | int | str]] = {
    "classify": {"temperature": 0.0, "top_p": 1.0, "max_tokens": 400, "reasoning_effort": "none"},
    "extract": {"temperature": 0.0, "top_p": 1.0, "max_tokens": 400, "reasoning_effort": "none"},
    "rewrite_query": {"temperature": 0.0, "top_p": 1.0, "max_tokens": 120, "reasoning_effort": "none"},
    "tool_select": {"temperature": 0.0, "top_p": 1.0, "max_tokens": 300, "reasoning_effort": "none"},
    "generate": {"temperature": 0.3, "top_p": 0.9, "max_tokens": 700, "reasoning_effort": "none"},
}
