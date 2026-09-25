"""Cấu hình chung cho bộ kiểm thử.

Nguyên tắc: **bộ kiểm thử phải chạy được mà không cần máy chủ suy luận.** Học
viên chạy pytest ở nhà, CI chạy trên runner không có GPU. Bài nào cần gọi model
thật được đánh dấu ``@pytest.mark.needs_llm`` và tự bỏ qua khi không có đường
chạy — nhưng phần lớn logic của hệ thống được thiết kế để kiểm thử được mà
không cần model, và đó là một tính chất của thiết kế chứ không phải may mắn.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Bộ kiểm thử không gọi model embedding: truy hồi luôn chạy ở chế độ keyword trừ khi bài kiểm thử tự đặt khác.
os.environ.setdefault("RETRIEVE_MODE", "keyword")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="session")
def train_tickets() -> list[dict]:
    """80 ticket huấn luyện."""
    from src.data import load_train

    return load_train()


@pytest.fixture(scope="session")
def adversarial_cases() -> list[dict]:
    """12 ca đối kháng."""
    from src.data import load_adversarial

    return load_adversarial()


@pytest.fixture()
def fake_llm():
    """Client giả trả về phản hồi định sẵn, không chạm mạng.

    Dùng để kiểm thử logic bao quanh model: lớp phòng vệ đầu ra, đường dự phòng
    theo luật, điều kiện chuyển người. Đây chính là phần mà bài học của khóa
    muốn nhấn: chất lượng hệ thống nằm ở tầng bao quanh model.
    """
    from src.llm.client import LLMResponse

    class FakeClient:
        def __init__(self, replies: list[str] | None = None) -> None:
            self.replies = replies or []
            self.calls: list[dict] = []
            self.calls_made = 0
            self.budget = 5

        def reset_budget(self) -> None:
            self.calls_made = 0

        def complete(self, *, task: str, system: str, user: str, params=None) -> LLMResponse:
            self.calls.append({"task": task, "system": system, "user": user})
            self.calls_made += 1
            text = self.replies.pop(0) if self.replies else "{}"
            return LLMResponse(
                text=text,
                task=task,
                model="fake",
                config_profile="T",
                from_cache=False,
                latency_ms=1,
                cache_key="fake",
            )

        def embed(self, texts: list[str]) -> list[list[float]]:
            return [[0.0] * 8 for _ in texts]

    return FakeClient
