"""Knowledge Sourcing — Discover, Ingest, Parse (slide 34 bước 1–2, slide 39 Documents → Parse).

Mỗi tài liệu trong ``data/knowledge/`` là một tệp Markdown có front-matter với ``doc_id``,
``version``, ``effective_date``, ``supersedes`` và ``status`` (SPEC-DATA-06). Module này chỉ
đọc và phân tích. Việc quyết định tài liệu nào còn được dùng thuộc về ``governance``.
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


def discover_documents(directory: str | Path | None = None) -> list[Path]:
    """Discover: liệt kê các tệp tài liệu trong kho, sắp theo tên."""
    base = Path(directory) if directory else ROOT / "data" / "knowledge"
    return sorted(base.glob("*.md"))


def ingest_document(path: Path) -> Document:
    """Ingest và Parse: đọc một tệp thành ``Document``.

    Raises:
        ValueError: Tệp thiếu front-matter hoặc thiếu trường bắt buộc.
    """
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    missing = [f for f in REQUIRED_FIELDS if not meta.get(f)]
    if missing:
        raise ValueError(f"{path.name}: thiếu trường front-matter {missing}")
    return Document(
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


def ingest_documents(directory: str | Path | None = None) -> list[Document]:
    """Đọc toàn bộ tài liệu trong kho, kể cả tài liệu đã bị thay thế.

    Đây là dữ liệu thô chưa qua Govern. Phần còn lại của hệ thống dùng
    ``governance.load_documents``.
    """
    return [ingest_document(path) for path in discover_documents(directory)]
