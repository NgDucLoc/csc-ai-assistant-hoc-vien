"""Lớp cache tất định cho mọi lời gọi model — SPEC-LLM-02.

Đây là hạ tầng, không phải tối ưu tốc độ. Ba thứ treo vào tệp cache này:

1. Tích hợp liên tục chạy được trên runner không có GPU, không có Ollama và
   không kết nối được tới server. Không có cache thì cổng chất lượng tự động
   ở Lab 5 là bất khả thi.
2. Lớp dự phòng thứ 3 khi mất cả hai đường suy luận (mục 4.5 kế hoạch buổi học).
3. Kết quả đánh giá tái lập được: cùng đầu vào luôn cho cùng đầu ra.

Khóa cache BẮT BUỘC bao gồm ``base_url`` và tên model. Nếu bỏ hai trường này,
kết quả sinh ở cấu hình S sẽ được dùng lại cho cấu hình L, và mọi so sánh giữa
hai cấu hình trở thành vô nghĩa mà không ai phát hiện ra.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS llm_cache (
    key            TEXT PRIMARY KEY,
    base_url       TEXT NOT NULL,
    model          TEXT NOT NULL,
    config_profile TEXT NOT NULL,
    task           TEXT NOT NULL,
    request_json   TEXT NOT NULL,
    response_text  TEXT NOT NULL,
    created_at     REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cache_profile ON llm_cache (config_profile);
CREATE INDEX IF NOT EXISTS idx_cache_task    ON llm_cache (task);
"""


class CacheMissError(RuntimeError):
    """Trượt cache trong khi CACHE_MODE=cache_only.

    Ở chế độ này việc gọi model bị cấm, nên trượt cache là lỗi chặn chứ không
    phải tình huống suy giảm. Thông báo phải nói rõ cách khắc phục vì lỗi này
    xuất hiện trong CI, nơi không có ai để hỏi.
    """


def make_key(
    *,
    base_url: str,
    model: str,
    task: str,
    messages: list[dict[str, str]],
    params: dict[str, Any],
) -> str:
    """Sinh khóa cache tất định từ toàn bộ thứ ảnh hưởng tới đầu ra.

    Args:
        base_url: Điểm cuối của máy chủ suy luận. BẮT BUỘC nằm trong khóa.
        model: Tên model. BẮT BUỘC nằm trong khóa.
        task: Tên tác vụ, dùng để thống kê và để xóa cache theo nhóm.
        messages: Danh sách message gửi lên model.
        params: Tham số sinh (nhiệt độ, top_p, max_tokens...).

    Returns:
        Chuỗi hex 64 ký tự.
    """
    payload = {
        "base_url": base_url,
        "model": model,
        "task": task,
        "messages": messages,
        "params": {k: params[k] for k in sorted(params)},
    }
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class LLMCache:
    """Kho cache SQLite, an toàn khi nhiều luồng worker cùng đọc ghi."""

    def __init__(self, path: str | Path) -> None:
        """Mở (hoặc tạo) tệp cache tại ``path``."""
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> str | None:
        """Trả về phản hồi đã lưu, hoặc None nếu chưa có."""
        with self._lock:
            row = self._conn.execute("SELECT response_text FROM llm_cache WHERE key = ?", (key,)).fetchone()
        if row is None:
            self.misses += 1
            return None
        self.hits += 1
        return str(row[0])

    def put(
        self,
        key: str,
        *,
        base_url: str,
        model: str,
        config_profile: str,
        task: str,
        request: dict[str, Any],
        response_text: str,
    ) -> None:
        """Lưu một phản hồi kèm đủ siêu dữ liệu để truy nguyên về sau."""
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO llm_cache "
                "(key, base_url, model, config_profile, task, request_json, response_text, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    key,
                    base_url,
                    model,
                    config_profile,
                    task,
                    json.dumps(request, ensure_ascii=False),
                    response_text,
                    time.time(),
                ),
            )
            self._conn.commit()

    def stats(self) -> dict[str, Any]:
        """Số liệu tóm tắt, dùng cho endpoint /metrics và cho báo cáo đánh giá."""
        with self._lock:
            total = self._conn.execute("SELECT COUNT(*) FROM llm_cache").fetchone()[0]
            by_profile = dict(
                self._conn.execute(
                    "SELECT config_profile, COUNT(*) FROM llm_cache GROUP BY config_profile"
                ).fetchall()
            )
        looked_up = self.hits + self.misses
        return {
            "entries": total,
            "by_profile": by_profile,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / looked_up, 4) if looked_up else None,
        }

    def purge_profile(self, config_profile: str) -> int:
        """Xóa toàn bộ mục cache sinh ra từ một cấu hình.

        Dùng khi số liệu đánh giá bị lẫn giữa hai cấu hình — tình huống được
        liệt kê trong bảng xử lý sự cố của Session 5.

        Returns:
            Số bản ghi đã xóa.
        """
        with self._lock:
            cur = self._conn.execute("DELETE FROM llm_cache WHERE config_profile = ?", (config_profile,))
            self._conn.commit()
            return cur.rowcount
