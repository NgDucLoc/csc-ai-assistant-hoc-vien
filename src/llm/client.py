"""Điểm truy cập DUY NHẤT tới model ngôn ngữ — SPEC-LLM-01, SPEC-ARCH-02.

Không được phép có lời gọi model nào nằm ngoài tệp này. ``tests/test_lab2.py``
có một bài kiểm thử quét mã nguồn để ép ràng buộc đó. Lý do không phải là
thẩm mỹ kiến trúc: cache, ghi nhật ký, đếm ngân sách gọi và ngắt mạch chỉ
hoạt động đồng nhất khi mọi lời gọi đi qua cùng một cửa.

Cả hai cấu hình đều phơi API tương thích OpenAI, nên chỉ cần một đường code.
Nếu hai đầu dùng hai giao thức khác nhau, lớp trừu tượng sẽ phình ra và đường
ít dùng sẽ không được kiểm thử — tức là hỏng đúng lúc cần đến.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from src.config import TASK_PARAMS, settings
from src.llm.cache import CacheMissError, LLMCache, make_key

log = logging.getLogger("csc.llm")


class BudgetExceededError(RuntimeError):
    """Vượt ngân sách gọi model trên một ticket — SPEC-INFRA-04."""


class CircuitOpenError(RuntimeError):
    """Ngắt mạch đang mở, không gọi model — SPEC-LLM-05."""


@dataclass
class LLMResponse:
    """Kết quả một lời gọi model, kèm siêu dữ liệu cần cho nhật ký và đánh giá."""

    text: str
    task: str
    model: str
    config_profile: str
    from_cache: bool
    latency_ms: int
    cache_key: str


class _CircuitBreaker:
    """Ngắt mạch đơn giản theo số lỗi liên tiếp — SPEC-LLM-05.

    Khi máy chủ suy luận treo giữa buổi, hệ thống phải suy giảm có kiểm soát
    (chuyển người) thay vì để 30 học viên cùng chờ hết thời gian chờ.
    """

    def __init__(self, threshold: int, cooldown: int) -> None:
        self.threshold = threshold
        self.cooldown = cooldown
        self.failures = 0
        self.opened_at: float | None = None

    def before_call(self) -> None:
        """Ném CircuitOpenError nếu mạch đang mở và chưa hết thời gian nghỉ."""
        if self.opened_at is None:
            return
        if time.time() - self.opened_at < self.cooldown:
            raise CircuitOpenError(
                f"Ngắt mạch đang mở sau {self.failures} lỗi liên tiếp. "
                f"Thử lại sau {self.cooldown} giây, hoặc đặt CACHE_MODE=cache_only."
            )
        self.opened_at = None
        self.failures = 0

    def on_success(self) -> None:
        """Đặt lại bộ đếm lỗi."""
        self.failures = 0
        self.opened_at = None

    def on_failure(self) -> None:
        """Tăng bộ đếm lỗi, mở mạch khi chạm ngưỡng."""
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = time.time()

    @property
    def is_open(self) -> bool:
        """True nếu mạch đang mở."""
        return self.opened_at is not None


class LLMClient:
    """Client thống nhất cho cả cấu hình S và cấu hình L."""

    def __init__(self, *, budget: int | None = None) -> None:
        """Khởi tạo client.

        Args:
            budget: Số lời gọi tối đa cho một ticket. Mặc định lấy từ cấu hình.
        """
        self.cache = LLMCache(settings.abs_path(settings.cache_path))
        self.breaker = _CircuitBreaker(settings.breaker_threshold, settings.breaker_cooldown)
        self.budget = budget if budget is not None else settings.max_llm_calls_per_ticket
        self.calls_made = 0
        self._http = httpx.Client(timeout=settings.llm_timeout)

    # -- ngân sách ---------------------------------------------------------
    def reset_budget(self) -> None:
        """Đặt lại bộ đếm khi bắt đầu xử lý một ticket mới."""
        self.calls_made = 0

    def _spend(self) -> None:
        if self.calls_made >= self.budget:
            raise BudgetExceededError(
                f"Đã dùng hết {self.budget} lời gọi model cho ticket này "
                f"(SPEC-INFRA-04). Gộp bước hoặc rút ngắn quy trình."
            )
        self.calls_made += 1

    # -- lời gọi chính -----------------------------------------------------
    def complete(
        self,
        *,
        task: str,
        system: str,
        user: str,
        params: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Gọi model sinh văn bản, đi qua cache và ngắt mạch.

        Args:
            task: Tên tác vụ, tra trong ``TASK_PARAMS`` nếu ``params`` bỏ trống.
            system: Prompt hệ thống.
            user: Nội dung người dùng, đã được phân tách bằng thẻ đánh dấu.
            params: Ghi đè tham số sinh.

        Returns:
            ``LLMResponse`` kèm cờ cho biết kết quả lấy từ cache hay gọi thật.

        Raises:
            CacheMissError: Trượt cache khi ``CACHE_MODE=cache_only``.
            BudgetExceededError: Vượt số lời gọi cho phép trên một ticket.
            CircuitOpenError: Ngắt mạch đang mở.
        """
        merged = dict(TASK_PARAMS.get(task, TASK_PARAMS["classify"]))
        if params:
            merged.update(params)

        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        key = make_key(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            task=task,
            messages=messages,
            params=merged,
        )

        started = time.perf_counter()

        if settings.cache_mode in ("on", "cache_only"):
            cached = self.cache.get(key)
            if cached is not None:
                return LLMResponse(
                    text=cached,
                    task=task,
                    model=settings.llm_model,
                    config_profile=settings.config_profile,
                    from_cache=True,
                    latency_ms=int((time.perf_counter() - started) * 1000),
                    cache_key=key,
                )

        if settings.cache_mode == "cache_only":
            raise CacheMissError(
                f"Trượt cache cho tác vụ '{task}' trong khi CACHE_MODE=cache_only.\n"
                f"  Khóa: {key[:16]}…\n"
                f"  Cấu hình: {settings.config_profile} · {settings.llm_model}\n"
                "Khắc phục: chạy 'uv run python scripts/warm_cache.py' trên máy có "
                "máy chủ suy luận, rồi commit lại .cache/llm_cache.db."
            )

        self._spend()
        self.breaker.before_call()
        try:
            text = self._call_remote(messages, merged)
            self.breaker.on_success()
        except (httpx.HTTPError, OSError) as exc:
            self.breaker.on_failure()
            log.warning("Lời gọi model thất bại (%s): %s", task, exc)
            raise

        if settings.cache_mode == "on":
            self.cache.put(
                key,
                base_url=settings.llm_base_url,
                model=settings.llm_model,
                config_profile=settings.config_profile,
                task=task,
                request={"messages": messages, "params": merged},
                response_text=text,
            )

        return LLMResponse(
            text=text,
            task=task,
            model=settings.llm_model,
            config_profile=settings.config_profile,
            from_cache=False,
            latency_ms=int((time.perf_counter() - started) * 1000),
            cache_key=key,
        )

    def _call_remote(self, messages: list[dict[str, str]], params: dict[str, Any]) -> str:
        """Gửi yêu cầu tới điểm cuối tương thích OpenAI."""
        resp = self._http.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json={"model": settings.llm_model, "messages": messages, **params},
        )
        resp.raise_for_status()
        data = resp.json()
        return str(data["choices"][0]["message"]["content"])

    # -- embedding ---------------------------------------------------------
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Tạo vector nhúng cho một lô văn bản.

        Model embedding cố ý giống nhau ở cả hai cấu hình (SPEC-INFRA-01), nên
        chỉ mục dựng ở cấu hình nào cũng đọc được ở cấu hình kia. Đây là ràng
        buộc tách bạch: quyết định hạ tầng không được ảnh hưởng tới kho tri thức.
        """
        resp = self._http.post(
            f"{settings.embed_base_url.rstrip('/')}/embeddings",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json={"model": settings.embed_model, "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]

    def health(self) -> dict[str, Any]:
        """Trạng thái đường chạy model, dùng cho endpoint /health và check_env."""
        return {
            "config_profile": settings.config_profile,
            "base_url": settings.llm_base_url,
            "model": settings.llm_model,
            "cache_mode": settings.cache_mode,
            "circuit_open": self.breaker.is_open,
            "calls_made": self.calls_made,
            "budget": self.budget,
            "cache": self.cache.stats(),
        }


_default_client: LLMClient | None = None


def get_client() -> LLMClient:
    """Trả về client dùng chung của tiến trình."""
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


def dump_response(resp: LLMResponse) -> str:
    """Tuần tự hóa một phản hồi để ghi vào nhật ký có cấu trúc."""
    return json.dumps(
        {
            "task": resp.task,
            "model": resp.model,
            "config_profile": resp.config_profile,
            "from_cache": resp.from_cache,
            "latency_ms": resp.latency_ms,
            "cache_key": resp.cache_key[:16],
        },
        ensure_ascii=False,
    )
