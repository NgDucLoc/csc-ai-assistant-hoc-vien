"""API bất đồng bộ cho ứng dụng AI — SPEC-ARCH-02 mục 5.

Mô hình đồng bộ không hợp lệ khi mỗi yêu cầu mất hàng chục giây. Điểm cuối
tiếp nhận trả về ``job_id`` ngay; xử lý diễn ra ở worker nền đọc hàng đợi
trong SQLite.

Đây là điểm khác biệt cụ thể nhất giữa API thường và API có thành phần AI:
độ trễ cao và biến động, nên hợp đồng giữa client và server phải là "nhận việc"
chứ không phải "trả kết quả".
"""

from __future__ import annotations

import threading
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agent.workflow import process_ticket
from src.config import settings
from src.guardrails.runtime import read_trace
from src.llm.client import get_client
from src.store import Store, get_store

_stop = threading.Event()


# --- worker nền ------------------------------------------------------------
def _worker_loop(store: Store, name: str) -> None:
    """Vòng lặp xử lý của một worker nền."""
    while not _stop.is_set():
        job = store.claim_next()
        if job is None:
            time.sleep(0.25)
            continue
        try:
            result = process_ticket(job["ticket_id"], job["ticket_text"])
            store.complete(job["job_id"], result.to_dict())
        except Exception as exc:  # noqa: BLE001 — worker không được chết vì một ticket
            store.fail(job["job_id"], f"{type(exc).__name__}: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Khởi động và dừng các worker nền cùng vòng đời ứng dụng."""
    store = get_store()
    threads = [
        threading.Thread(target=_worker_loop, args=(store, f"w{i}"), daemon=True)
        for i in range(settings.api_workers)
    ]
    for t in threads:
        t.start()
    yield
    _stop.set()


app = FastAPI(
    title="Trợ lý xử lý ticket CSKH",
    description=(
        "API hỗ trợ giao dịch viên phân loại, tra cứu và soạn dự thảo phản hồi. "
        "Hệ thống KHÔNG gửi phản hồi tới khách hàng; mọi dự thảo phải qua người duyệt."
    ),
    version="0.6.0",
    lifespan=lifespan,
)


# --- lược đồ ---------------------------------------------------------------
class TicketIn(BaseModel):
    """Ticket gửi vào hệ thống."""

    ticket_id: str = Field(..., min_length=3, max_length=32, examples=["TK-00042"])
    text: str = Field(..., min_length=1, max_length=4000)


class JobAccepted(BaseModel):
    """Phản hồi khi hệ thống đã nhận việc."""

    job_id: str
    state: str
    poll_url: str


class ReviewIn(BaseModel):
    """Thao tác duyệt của giao dịch viên."""

    action: str = Field(..., pattern="^(approve|edit_approve|reject)$")
    reviewer: str = Field(..., min_length=1, max_length=64)
    reason: str | None = None
    edited_text: str | None = None


# --- điểm cuối -------------------------------------------------------------
@app.post("/tickets", response_model=JobAccepted, status_code=202)
def submit_ticket(payload: TicketIn) -> JobAccepted:
    """Nhận một ticket và trả về mã công việc ngay lập tức."""
    job_id = get_store().enqueue(payload.ticket_id, payload.text)
    return JobAccepted(job_id=job_id, state="queued", poll_url=f"/jobs/{job_id}")


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    """Tra cứu trạng thái và kết quả của một công việc."""
    job = get_store().get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy công việc {job_id}")
    return job


@app.get("/review/queue")
def review_queue(limit: int = 50) -> dict[str, Any]:
    """Danh sách ticket đang chờ người duyệt."""
    items = get_store().list_pending_review(limit)
    return {"count": len(items), "items": items}


@app.post("/review/{job_id}")
def submit_review(job_id: str, payload: ReviewIn) -> dict[str, Any]:
    """Ghi nhận thao tác duyệt của giao dịch viên — SPEC-FLOW-04.

    Đây là điểm DUY NHẤT trong hệ thống mà một dự thảo chuyển sang trạng thái
    được chấp thuận. Không có đường nào khác dẫn tới đó (SPEC-FLOW-03).
    """
    store = get_store()
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy công việc {job_id}")
    if job["state"] != "done":
        raise HTTPException(status_code=409, detail=f"Công việc đang ở trạng thái '{job['state']}'")

    result = job.get("result") or {}
    try:
        action_id = store.record_review(
            job_id=job_id,
            ticket_id=job["ticket_id"],
            trace_id=result.get("trace_id"),
            action=payload.action,
            reviewer=payload.reviewer,
            reason=payload.reason,
            original=(result.get("draft") or {}).get("text"),
            edited=payload.edited_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"action_id": action_id, "job_id": job_id, "action": payload.action}


@app.get("/trace/{trace_id}")
def get_trace(trace_id: str) -> dict[str, Any]:
    """Tái dựng toàn bộ vòng đời xử lý của một ticket — tiêu chí nghiệm thu Lab 5."""
    events = read_trace(trace_id)
    if not events:
        raise HTTPException(status_code=404, detail=f"Không có nhật ký cho {trace_id}")
    return {"trace_id": trace_id, "event_count": len(events), "events": events}


@app.get("/health")
def health() -> dict[str, Any]:
    """Kiểm tra sức khỏe hệ thống."""
    return {"status": "ok", "profile": settings.profile_banner(), **get_client().health()}


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    """Chỉ số vận hành, gồm cả tín hiệu suy giảm chất lượng từ người duyệt."""
    store = get_store()
    return {
        "config_profile": settings.config_profile,
        "queue": store.queue_depth(),
        "review": store.review_stats(),
        "cache": get_client().cache.stats(),
    }
