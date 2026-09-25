"""Knowledge Governance — vòng đời tài liệu (slide 34 bước 5, slide 33 thuộc tính Fresh và Governed).

Kho có hai cặp tài liệu chính sách mâu thuẫn nhau, bản cũ chưa được gỡ (SPEC-DATA-05). Nhóm nào
truy hồi mà không lọc theo ``status`` sẽ trích dẫn chính sách đã hết hiệu lực, và hệ thống trả lời
khách hàng bằng mức bồi thường sai. Quản lý tri thức doanh nghiệp là vấn đề vòng đời tài liệu,
không chỉ là vấn đề tìm kiếm (SPEC-DATA-06).
"""

from __future__ import annotations

from pathlib import Path

from src.knowledge.sourcing import Document, ingest_documents


def is_current(doc: Document) -> bool:
    """Tài liệu còn hiệu lực khi ``status`` là ``active``."""
    return doc.status == "active"


def load_documents(
    directory: str | Path | None = None, *, include_superseded: bool = False
) -> list[Document]:
    """Nạp các tài liệu được phép dùng.

    Args:
        directory: Thư mục chứa tài liệu. Mặc định ``data/knowledge``.
        include_superseded: Nếu False (mặc định), bỏ qua tài liệu đã bị thay thế. Đặt True khi
            muốn thấy hậu quả của việc không lọc.

    Returns:
        Danh sách tài liệu, sắp theo tên tệp.
    """
    docs = ingest_documents(directory)
    return docs if include_superseded else [d for d in docs if is_current(d)]


def conflict_report(directory: str | Path | None = None) -> list[dict[str, str]]:
    """Liệt kê các cặp tài liệu cũ và mới để đối chiếu."""
    docs = ingest_documents(directory)
    by_id = {d.doc_id: d for d in docs}
    pairs: list[dict[str, str]] = []
    for doc in docs:
        if doc.supersedes and doc.supersedes in by_id:
            old = by_id[doc.supersedes]
            pairs.append(
                {
                    "new_doc": doc.doc_id,
                    "new_version": doc.version,
                    "new_effective": doc.effective_date,
                    "old_doc": old.doc_id,
                    "old_version": old.version,
                    "old_status": old.status,
                    "title": doc.title,
                }
            )
    return pairs
