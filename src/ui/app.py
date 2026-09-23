"""Màn hình duyệt cho giao dịch viên — SPEC-FLOW-04.

Ba màn hình: gửi ticket, hàng đợi duyệt, và trang theo dõi.

Thiết kế quan trọng nhất ở đây không phải bố cục mà là **thứ tự thông tin**:
người duyệt thấy ticket gốc và các đoạn tri thức đã truy hồi TRƯỚC khi thấy
dự thảo. Nếu đặt dự thảo lên đầu, người duyệt sẽ đọc dự thảo rồi tìm cách
biện minh cho nó thay vì kiểm chứng nó — và thao tác duyệt mất hết giá trị
làm tín hiệu chất lượng.

Chạy: uv run streamlit run src/ui/app.py
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.agent.workflow import process_ticket
from src.config import settings
from src.store import get_store

st.set_page_config(page_title="Trợ lý ticket CSKH", layout="wide")

REASON_LABELS = {
    "do_tin_cay_thap": "Độ tin cậy phân loại thấp",
    "khong_du_can_cu": "Không đủ căn cứ trong kho tri thức",
    "tranh_chap_tien": "Có tranh chấp về tiền",
    "muc_uu_tien_cao_nhat": "Ticket mức ưu tiên cao nhất",
    "guardrail_dau_vao": "Guardrail đầu vào kích hoạt",
    "guardrail_dau_ra": "Guardrail đầu ra kích hoạt",
    "he_thong_suy_giam": "Hệ thống suy giảm, không xử lý được",
}


def _banner() -> None:
    """Hiện cấu hình đang chạy — SPEC-INFRA-03 buộc phải nhìn thấy được."""
    st.caption(f"⚙️ {settings.profile_banner()}")


def page_submit() -> None:
    """Màn hình gửi ticket và xem kết quả xử lý ngay."""
    st.header("Gửi ticket")
    with st.form("submit"):
        ticket_id = st.text_input("Mã ticket", value="TK-99001")
        text = st.text_area("Nội dung khách hàng gửi", height=180)
        submitted = st.form_submit_button("Xử lý")
    if not submitted or not text.strip():
        return

    with st.spinner("Đang xử lý…"):
        result = process_ticket(ticket_id, text)
    store = get_store()
    job_id = store.enqueue(ticket_id, text)
    store.complete(job_id, result.to_dict())
    st.success(f"Xong · trạng thái **{result.status.value}** · trace `{result.trace_id}`")
    _render_result(result.to_dict())


def _render_result(data: dict[str, Any]) -> None:
    """Hiện kết quả xử lý theo đúng thứ tự: gốc → căn cứ → dự thảo."""
    cls = data.get("classification") or {}
    if cls:
        cols = st.columns(4)
        cols[0].metric("Nhóm vấn đề", cls.get("category", "—"))
        cols[1].metric("Ưu tiên", cls.get("priority", "—"))
        cols[2].metric("Sắc thái", cls.get("sentiment", "—"))
        cols[3].metric("Độ tin cậy", f"{cls.get('confidence', 0):.2f}")
        if cls.get("defense_layer") != "direct":
            st.warning(
                f"Đầu ra có cấu trúc phải cứu bằng lớp phòng vệ "
                f"`{cls.get('defense_layer')}` sau {cls.get('attempts')} lần thử."
            )

    reasons = data.get("escalation_reasons") or []
    if reasons:
        st.error("**Chuyển giao dịch viên** vì: " + " · ".join(REASON_LABELS.get(r, r) for r in reasons))

    hits = data.get("retrieval") or []
    st.subheader(f"Căn cứ đã truy hồi ({len(hits)} đoạn)")
    if not hits:
        st.info("Không truy hồi được đoạn tri thức nào.")
    for hit in hits:
        with st.expander(f"{hit['citation']} · {hit['section']} · điểm {hit['score']:.3f}"):
            st.write(hit["text"])

    calls = data.get("tool_calls") or []
    if calls:
        st.subheader("Công cụ đã gọi")
        st.dataframe(
            [
                {
                    "công cụ": c["name"],
                    "nguồn": c["source"],
                    "kết quả": "ok" if c["ok"] else f"lỗi: {c['error']}",
                    "ms": c["latency_ms"],
                }
                for c in calls
            ],
            use_container_width=True,
        )

    draft = data.get("draft") or {}
    st.subheader("Dự thảo phản hồi")
    if draft.get("text"):
        st.write(draft["text"])
        if draft.get("invalid_citations"):
            st.error(f"Trích dẫn không có trong ngữ cảnh: {draft['invalid_citations']}")
    else:
        st.info(draft.get("reason") or "Không sinh dự thảo.")

    gout = (data.get("guardrails") or {}).get("output") or {}
    if gout.get("violations"):
        st.error("Guardrail đầu ra: " + " · ".join(gout["violations"]))
    if gout.get("warnings"):
        st.warning("Cần lưu ý: " + " · ".join(gout["warnings"]))


def page_review() -> None:
    """Hàng đợi duyệt với ba lựa chọn: duyệt, sửa rồi duyệt, từ chối."""
    st.header("Hàng đợi duyệt")
    store = get_store()
    items = store.list_pending_review()
    if not items:
        st.info("Không có ticket nào chờ duyệt.")
        return

    reviewer = st.text_input("Tên người duyệt", value="gdv01")
    for item in items:
        with st.container(border=True):
            st.markdown(f"**{item['ticket_id']}** · trace `{item.get('trace_id', '—')}`")
            _render_result(item)

            original = (item.get("draft") or {}).get("text", "")
            edited = st.text_area(
                "Sửa dự thảo trước khi duyệt",
                value=original,
                key=f"edit-{item['job_id']}",
                height=140,
            )
            reason = st.text_input("Lý do (bắt buộc khi từ chối)", key=f"reason-{item['job_id']}")

            c1, c2, c3 = st.columns(3)
            if c1.button("Duyệt", key=f"a-{item['job_id']}"):
                store.record_review(
                    job_id=item["job_id"],
                    ticket_id=item["ticket_id"],
                    trace_id=item.get("trace_id"),
                    action="approve",
                    reviewer=reviewer,
                    original=original,
                )
                st.rerun()
            if c2.button("Sửa rồi duyệt", key=f"e-{item['job_id']}"):
                store.record_review(
                    job_id=item["job_id"],
                    ticket_id=item["ticket_id"],
                    trace_id=item.get("trace_id"),
                    action="edit_approve",
                    reviewer=reviewer,
                    original=original,
                    edited=edited,
                )
                st.rerun()
            if c3.button("Từ chối", key=f"r-{item['job_id']}"):
                if not reason.strip():
                    st.error("Từ chối bắt buộc kèm lý do.")
                else:
                    store.record_review(
                        job_id=item["job_id"],
                        ticket_id=item["ticket_id"],
                        trace_id=item.get("trace_id"),
                        action="reject",
                        reviewer=reviewer,
                        reason=reason,
                        original=original,
                    )
                    st.rerun()


def page_monitor() -> None:
    """Trang theo dõi: tỉ lệ sửa và từ chối là tín hiệu suy giảm sớm nhất."""
    st.header("Theo dõi chất lượng")
    stats = get_store().review_stats()
    if not stats["total"]:
        st.info("Chưa có thao tác duyệt nào để thống kê.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Tỉ lệ duyệt thẳng", f"{(stats['approve_rate'] or 0) * 100:.1f}%")
    c2.metric("Tỉ lệ phải sửa", f"{(stats['edit_rate'] or 0) * 100:.1f}%")
    c3.metric("Tỉ lệ từ chối", f"{(stats['reject_rate'] or 0) * 100:.1f}%")

    st.caption(
        "Tỉ lệ sửa tăng mà điểm đánh giá tự động không đổi là dấu hiệu phân bố "
        "ticket đã dịch chuyển hoặc chính sách vừa được cập nhật — SPEC-RESP-03."
    )
    if stats["top_reject_reasons"]:
        st.subheader("Lý do từ chối thường gặp")
        st.dataframe(stats["top_reject_reasons"], use_container_width=True)


PAGES = {"Gửi ticket": page_submit, "Hàng đợi duyệt": page_review, "Theo dõi": page_monitor}

st.sidebar.title("Trợ lý ticket CSKH")
_banner()
choice = st.sidebar.radio("Màn hình", list(PAGES))
st.sidebar.divider()
st.sidebar.caption(
    "Hệ thống hỗ trợ giao dịch viên. Không có đường nào gửi phản hồi tới khách "
    "hàng mà chưa qua thao tác duyệt của con người."
)
PAGES[choice]()
