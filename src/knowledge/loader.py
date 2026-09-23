"""Nạp kho tri thức và xử lý vòng đời tài liệu — SPEC-DATA-06.

Mỗi tài liệu trong ``data/knowledge/`` mang front-matter với ``version``,
``effective_date``, ``supersedes`` và ``status``. Bốn trường này tồn tại để
giải quyết một bẫy được cài có chủ ý trong dữ liệu: **hai cặp tài liệu chính
sách mâu thuẫn nhau, bản cũ chưa được gỡ khỏi kho** (SPEC-DATA-05).

Đây là tình huống có thật trong mọi doanh nghiệp. Nhóm nào truy hồi mà không
lọc theo ``status`` sẽ trích dẫn chính sách đã hết hiệu lực, và hệ thống sẽ
trả lời khách hàng bằng mức bồi thường sai. Bài học: quản lý tri thức doanh
nghiệp là vấn đề vòng đời tài liệu, không phải vấn đề tìm kiếm.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import ROOT

_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

REQUIRED_FIELDS = ("doc_id", "title", "category", "version", "effective_date", "status")


@dataclass
class Document:
    """Một tài liệu tri thức đã nạp."""

    doc_id: str
    title: str
    category: str
    version: str
    effective_date: str
    status: str
    supersedes: str | None
    body: str
    path: Path

    @property
    def is_active(self) -> bool:
        """True nếu tài liệu còn hiệu lực."""
        return self.status == "active"


def _parse_scalar(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    return None if value in ("", "null", "~") else value


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Tách front-matter khỏi phần thân tài liệu.

    Args:
        text: Toàn bộ nội dung tệp Markdown.

    Returns:
        Cặp (siêu dữ liệu, phần thân).

    Raises:
        ValueError: Tệp không có front-matter.
    """
    match = _FRONT_MATTER.match(text)
    if not match:
        raise ValueError("Tài liệu thiếu front-matter YAML (SPEC-DATA-06)")
    meta: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = _parse_scalar(value)
    return meta, text[match.end() :]


def load_documents(
    directory: str | Path | None = None, *, include_superseded: bool = False
) -> list[Document]:
    """Nạp toàn bộ tài liệu tri thức.

    Args:
        directory: Thư mục chứa tài liệu. Mặc định ``data/knowledge``.
        include_superseded: Nếu False (mặc định), bỏ qua tài liệu đã bị thay
            thế. Đặt True khi muốn cho học viên thấy hậu quả của việc không lọc.

    Returns:
        Danh sách tài liệu, sắp theo ``doc_id``.

    Raises:
        ValueError: Có tài liệu thiếu trường bắt buộc.
    """
    base = Path(directory) if directory else ROOT / "data" / "knowledge"
    docs: list[Document] = []
    for path in sorted(base.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        missing = [f for f in REQUIRED_FIELDS if not meta.get(f)]
        if missing:
            raise ValueError(f"{path.name}: thiếu trường front-matter {missing}")
        doc = Document(
            doc_id=str(meta["doc_id"]),
            title=str(meta["title"]),
            category=str(meta["category"]),
            version=str(meta["version"]),
            effective_date=str(meta["effective_date"]),
            status=str(meta["status"]),
            supersedes=meta.get("supersedes"),
            body=body.strip(),
            path=path,
        )
        if doc.status != "active" and not include_superseded:
            continue
        docs.append(doc)
    return docs


def conflict_report(directory: str | Path | None = None) -> list[dict[str, str]]:
    """Liệt kê các cặp tài liệu cũ–mới để đối chiếu.

    Dùng ở Session 3 khi giảng phần quản lý phiên bản tri thức: cho học viên
    chạy hàm này để thấy chính xác hai cặp bẫy nằm ở đâu, sau khi họ đã tự
    vấp phải hậu quả của việc không lọc.
    """
    docs = load_documents(directory, include_superseded=True)
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
