"""Hàng đợi công việc, kết quả và nhật ký thao tác duyệt — SPEC-ARCH-02, SPEC-FLOW-04.

Trạng thái nằm ngoài tiến trình (SQLite), không giữ trong bộ nhớ. Hai lý do:
worker khởi động lại không mất việc đang chờ, và tầng API mở rộng ngang được
độc lập với tầng xử lý.

Về bảng ``review_actions``: nhật ký thao tác duyệt **không phải để giao diện
trông đầy đủ**. Tỉ lệ sửa và lý do từ chối là chỉ số chất lượng đáng tin cậy
nhất mà hệ thống có — đáng tin hơn cả điểm đánh giá tự động, vì nó phản ánh
phán đoán của người thật trên ca thật. Đây là nguồn dữ liệu chính cho sprint
cải tiến ở Session 6 và là tín hiệu phát hiện suy giảm sớm nhất ở Session 5.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from src.config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id      TEXT PRIMARY KEY,
    ticket_id   TEXT NOT NULL,
    ticket_text TEXT NOT NULL,
    state       TEXT NOT NULL,          -- queued | running | done | failed
    result_json TEXT,
    error       TEXT,
    created_at  REAL NOT NULL,
    started_at  REAL,
    finished_at REAL
);
CREATE INDEX IF NOT EXISTS idx_jobs_state ON jobs (state);

CREATE TABLE IF NOT EXISTS review_actions (
    action_id   TEXT PRIMARY KEY,
    job_id      TEXT NOT NULL,
    ticket_id   TEXT NOT NULL,
    trace_id    TEXT,
    action      TEXT NOT NULL,          -- approve | edit_approve | reject
    reviewer    TEXT NOT NULL,
    reason      TEXT,
    original    TEXT,
    edited      TEXT,
    created_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_review_action ON review_actions (action);
"""


class Store:
    """Kho lưu trữ SQLite dùng chung cho API, worker và giao diện."""

    def __init__(self, path: str | Path | None = None) -> None:
        """Mở (hoặc tạo) cơ sở dữ liệu."""
        self.path = Path(path) if path else settings.abs_path(settings.db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # -- hàng đợi ----------------------------------------------------------
    def enqueue(self, ticket_id: str, ticket_text: str) -> str:
        """Nhận một ticket vào hàng đợi và trả về mã công việc ngay lập tức."""
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        with self._lock:
            self._conn.execute(
                "INSERT INTO jobs (job_id, ticket_id, ticket_text, state, created_at) "
                "VALUES (?, ?, ?, 'queued', ?)",
                (job_id, ticket_id, ticket_text, time.time()),
            )
            self._conn.commit()
        return job_id

    def claim_next(self) -> dict[str, Any] | None:
        """Lấy một công việc chờ và đánh dấu đang chạy.

        Dùng giao dịch IMMEDIATE để hai worker không cùng nhận một việc.
        """
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            row = self._conn.execute(
                "SELECT * FROM jobs WHERE state = 'queued' ORDER BY created_at LIMIT 1"
            ).fetchone()
            if row is None:
                self._conn.commit()
                return None
            self._conn.execute(
                "UPDATE jobs SET state = 'running', started_at = ? WHERE job_id = ?",
                (time.time(), row["job_id"]),
            )
            self._conn.commit()
        return dict(row)

    def complete(self, job_id: str, result: dict[str, Any]) -> None:
        """Ghi kết quả thành công của một công việc."""
        with self._lock:
            self._conn.execute(
                "UPDATE jobs SET state = 'done', result_json = ?, finished_at = ? WHERE job_id = ?",
                (json.dumps(result, ensure_ascii=False, default=str), time.time(), job_id),
            )
            self._conn.commit()

    def fail(self, job_id: str, error: str) -> None:
        """Ghi lỗi của một công việc."""
        with self._lock:
            self._conn.execute(
                "UPDATE jobs SET state = 'failed', error = ?, finished_at = ? WHERE job_id = ?",
                (error, time.time(), job_id),
            )
            self._conn.commit()

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Tra cứu trạng thái và kết quả một công việc."""
        with self._lock:
            row = self._conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        data = dict(row)
        if data.get("result_json"):
            data["result"] = json.loads(data.pop("result_json"))
        else:
            data.pop("result_json", None)
            data["result"] = None
        return data

    def list_pending_review(self, limit: int = 50) -> list[dict[str, Any]]:
        """Danh sách ticket đã xử lý xong và đang chờ người duyệt."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT job_id, ticket_id, result_json FROM jobs "
                "WHERE state = 'done' ORDER BY finished_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        out: list[dict[str, Any]] = []
        reviewed = self.reviewed_job_ids()
        for row in rows:
            if row["job_id"] in reviewed:
                continue
            out.append(
                {
                    "job_id": row["job_id"],
                    "ticket_id": row["ticket_id"],
                    **json.loads(row["result_json"]),
                }
            )
        return out

    def queue_depth(self) -> dict[str, int]:
        """Số công việc theo từng trạng thái, dùng cho /metrics."""
        with self._lock:
            rows = self._conn.execute("SELECT state, COUNT(*) c FROM jobs GROUP BY state").fetchall()
        return {r["state"]: r["c"] for r in rows}

    # -- nhật ký duyệt -----------------------------------------------------
    def record_review(
        self,
        *,
        job_id: str,
        ticket_id: str,
        trace_id: str | None,
        action: str,
        reviewer: str,
        reason: str | None = None,
        original: str | None = None,
        edited: str | None = None,
    ) -> str:
        """Ghi lại một thao tác duyệt — SPEC-FLOW-04.

        Args:
            job_id: Mã công việc đã xử lý xong.
            ticket_id: Mã ticket tương ứng.
            trace_id: Mã truy vết, để nối thao tác duyệt với nhật ký xử lý.
            action: ``approve``, ``edit_approve`` hoặc ``reject``.
            reviewer: Định danh người duyệt.
            reason: Bắt buộc khi ``action='reject'``.
            original: Dự thảo gốc do hệ thống sinh.
            edited: Nội dung sau khi người duyệt sửa, nếu có.

        Returns:
            Mã thao tác.

        Raises:
            ValueError: Hành động không hợp lệ, hoặc từ chối mà không nêu lý do.
        """
        # TODO(LAB-4): SPEC-FLOW-04 — ghi thao tác duyệt; từ chối bắt buộc kèm lý do
        #   Chạy "uv run pytest -m lab4" để biết mình đã đúng chưa.
        raise NotImplementedError("LAB-4: SPEC-FLOW-04 — ghi thao tác duyệt; từ chối bắt buộc kèm lý do")

    def reviewed_job_ids(self) -> set[str]:
        """Tập mã công việc đã có người duyệt."""
        with self._lock:
            rows = self._conn.execute("SELECT DISTINCT job_id FROM review_actions").fetchall()
        return {r["job_id"] for r in rows}

    def review_stats(self) -> dict[str, Any]:
        """Tỉ lệ duyệt, sửa và từ chối — tín hiệu suy giảm chất lượng sớm nhất.

        SPEC-RESP-03 dùng chính hai tỉ lệ này làm ngưỡng cảnh báo. Khi tỉ lệ sửa
        tăng mà điểm đánh giá tự động không đổi, nguyên nhân thường là phân bố
        ticket đã dịch chuyển hoặc chính sách vừa được cập nhật.
        """
        with self._lock:
            rows = self._conn.execute(
                "SELECT action, COUNT(*) c FROM review_actions GROUP BY action"
            ).fetchall()
            reasons = self._conn.execute(
                "SELECT reason, COUNT(*) c FROM review_actions "
                "WHERE action = 'reject' AND reason IS NOT NULL GROUP BY reason ORDER BY c DESC LIMIT 5"
            ).fetchall()
        counts = {r["action"]: r["c"] for r in rows}
        total = sum(counts.values())
        return {
            "total": total,
            "counts": counts,
            "approve_rate": round(counts.get("approve", 0) / total, 4) if total else None,
            "edit_rate": round(counts.get("edit_approve", 0) / total, 4) if total else None,
            "reject_rate": round(counts.get("reject", 0) / total, 4) if total else None,
            "top_reject_reasons": [{"reason": r["reason"], "count": r["c"]} for r in reasons],
        }


_default: Store | None = None


def get_store() -> Store:
    """Trả về kho lưu trữ dùng chung của tiến trình."""
    global _default
    if _default is None:
        _default = Store()
    return _default
