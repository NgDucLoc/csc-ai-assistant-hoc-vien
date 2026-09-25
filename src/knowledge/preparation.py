"""Knowledge Preparation — Prepare, Organize & Enrich (slide 34 bước 3–4, slide 39 Chunk → Enrich Metadata).

Chiến lược chia đoạn: **theo cấu trúc mục, không theo số ký tự cố định** (SPEC-RAG-01). Tài liệu
chính sách viễn thông có cấu trúc mục rõ ràng, và một điều khoản bị cắt làm đôi giữa chừng sẽ mất
nghĩa (slide 41: đoạn quá nhỏ mất ngữ cảnh, quá lớn nhiều nhiễu, đoạn tốt là một đơn vị trọn ý).

Mỗi đoạn mang đủ siêu dữ liệu để truy ngược về tài liệu gốc (SPEC-RAG-04). Tiêu đề tài liệu và
tiêu đề mục được ghép vào đầu văn bản khi nhúng, vì truy vấn của khách hàng thường nhắc tên gói
cước hoặc tên chính sách chứ không nhắc nội dung điều khoản.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.config import settings
from src.knowledge.governance import load_documents
from src.knowledge.sourcing import Document

_HEADING = re.compile(r"^(#{1,4})\s+(.*)$", re.MULTILINE)


@dataclass
class Chunk:
    """Một đoạn tài liệu sẵn sàng để nhúng."""

    chunk_id: str
    doc_id: str
    doc_title: str
    section: str
    category: str
    version: str
    effective_date: str
    text: str

    def embedding_text(self) -> str:
        """Văn bản thực sự đem đi nhúng, có tiêu đề dẫn đầu."""
        return f"{self.doc_title} — {self.section}\n{self.text}"


def split_sections(doc: Document) -> list[tuple[str, str]]:
    """Cắt phần thân tài liệu thành các cặp (tiêu đề mục, nội dung)."""
    matches = list(_HEADING.finditer(doc.body))
    if not matches:
        return [(doc.title, doc.body.strip())]
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(doc.body)
        content = doc.body[start:end].strip()
        if content:
            sections.append((m.group(2).strip(), content))
    return sections


def chunk_document(doc: Document, *, max_chars: int | None = None, overlap: int | None = None) -> list[Chunk]:
    """Chia một tài liệu thành các đoạn.

    Mục dài hơn ``max_chars`` được cắt tiếp theo ranh giới câu, có phần chồng lấn để không mất
    ngữ cảnh ở chỗ nối.

    Args:
        doc: Tài liệu đã nạp.
        max_chars: Độ dài tối đa mỗi đoạn. Mặc định lấy từ cấu hình.
        overlap: Số ký tự chồng lấn giữa hai đoạn liền nhau.

    Returns:
        Danh sách đoạn kèm đầy đủ siêu dữ liệu để trích dẫn được.
    """
    # TODO(LAB-3): Prepare — chia đoạn theo cấu trúc mục, giữ đủ siêu dữ liệu để trích dẫn
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Prepare — chia đoạn theo cấu trúc mục, giữ đủ siêu dữ liệu để trích dẫn")


def _split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    sentences = re.split(r"(?<=[.!?;:])\s+", text)
    out: list[str] = []
    buf = ""
    for sent in sentences:
        if len(buf) + len(sent) + 1 <= max_chars:
            buf = f"{buf} {sent}".strip()
        else:
            if buf:
                out.append(buf)
            buf = (buf[-overlap:] + " " + sent).strip() if overlap and buf else sent
    if buf:
        out.append(buf)
    return out


def build_chunks(directory: str | Path | None = None) -> list[Chunk]:
    """Nạp kho tri thức (chỉ tài liệu còn hiệu lực) và chia đoạn toàn bộ."""
    chunks: list[Chunk] = []
    for doc in load_documents(directory):
        chunks.extend(chunk_document(doc))
    return chunks
