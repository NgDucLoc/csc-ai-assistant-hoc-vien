"""Chia đoạn và dựng chỉ mục vector — SPEC-RAG-01.

Chiến lược chia đoạn: **theo cấu trúc mục, không theo số ký tự cố định**.
Tài liệu chính sách viễn thông có cấu trúc mục rõ ràng, và một điều khoản bị
cắt làm đôi giữa chừng sẽ mất nghĩa. Mỗi đoạn được gắn tiêu đề tài liệu và
tiêu đề mục lên đầu — thí nghiệm ở Session 3 bước 4 cho thấy riêng thay đổi
này đã nâng Recall@5 đáng kể, vì truy vấn của khách hàng thường nhắc tên gói
cước hoặc tên chính sách chứ không nhắc nội dung điều khoản.

Chỉ mục lưu bằng Chroma nếu có, và có đường lùi sang chỉ mục JSON thuần Python
khi chưa cài được Chroma. Đường lùi này không phải để tiết kiệm: nó là thứ giữ
cho Lab 3 chạy được trên máy học viên gặp trục trặc cài đặt.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.config import settings
from src.knowledge.loader import Document, load_documents

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

    Mục dài hơn ``max_chars`` được cắt tiếp theo ranh giới câu, có phần chồng
    lấn để không mất ngữ cảnh ở chỗ nối.

    Args:
        doc: Tài liệu đã nạp.
        max_chars: Độ dài tối đa mỗi đoạn. Mặc định lấy từ cấu hình.
        overlap: Số ký tự chồng lấn giữa hai đoạn liền nhau.

    Returns:
        Danh sách đoạn kèm đầy đủ siêu dữ liệu để trích dẫn được.
    """
    # TODO(LAB-3): Chia đoạn theo cấu trúc mục, gắn tiêu đề tài liệu vào đầu mỗi đoạn
    #   Chạy "uv run pytest -m lab3" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-3: Chia đoạn theo cấu trúc mục, gắn tiêu đề tài liệu vào đầu mỗi đoạn")


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
    """Nạp kho tri thức và chia đoạn toàn bộ tài liệu còn hiệu lực."""
    chunks: list[Chunk] = []
    for doc in load_documents(directory):
        chunks.extend(chunk_document(doc))
    return chunks


# --- lưu trữ chỉ mục -------------------------------------------------------
def _chroma_collection(path: Path, *, reset: bool = False) -> Any:
    import chromadb  # nhập muộn: Lab 1 và Lab 2 chưa cần Chroma

    client = chromadb.PersistentClient(path=str(path))
    name = "knowledge"
    if reset:
        try:
            client.delete_collection(name)
        except Exception:  # noqa: BLE001 — chưa tồn tại thì bỏ qua
            pass
    return client.get_or_create_collection(name, metadata={"hnsw:space": "cosine"})


def build_index(
    *, out_path: str | Path | None = None, reset: bool = True, verbose: bool = True
) -> dict[str, Any]:
    """Dựng chỉ mục vector từ kho tri thức.

    Mất khoảng 2–4 phút trên CPU cho ~300 đoạn. Vì lý do đó ``data/index_prebuilt/``
    là mặc định của lớp học, còn hàm này để học viên xác minh mình dựng lại được.

    Returns:
        Bản tóm tắt số đoạn, số tài liệu và cấu hình đã dùng.
    """
    from src.llm.client import get_client

    target = Path(out_path) if out_path else settings.abs_path(settings.chroma_path)
    target.mkdir(parents=True, exist_ok=True)
    chunks = build_chunks()
    client = get_client()

    texts = [c.embedding_text() for c in chunks]
    vectors: list[list[float]] = []
    batch = 16
    for i in range(0, len(texts), batch):
        vectors.extend(client.embed(texts[i : i + batch]))
        if verbose:
            print(f"  đã nhúng {min(i + batch, len(texts))}/{len(texts)} đoạn")

    try:
        col = _chroma_collection(target, reset=reset)
        col.add(
            ids=[c.chunk_id for c in chunks],
            embeddings=vectors,
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "doc_id": c.doc_id,
                    "doc_title": c.doc_title,
                    "section": c.section,
                    "category": c.category,
                    "version": c.version,
                    "effective_date": c.effective_date,
                }
                for c in chunks
            ],
        )
        backend = "chroma"
    except ImportError:
        backend = "json"

    # Luôn ghi bản JSON song song: đây là đường lùi và cũng là thứ commit được.
    payload = {
        "config_profile": settings.config_profile,
        "embed_model": settings.embed_model,
        "chunk_size": settings.chunk_size,
        "chunks": [{**asdict(c), "embedding": v} for c, v in zip(chunks, vectors, strict=True)],
    }
    (target / "index.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    return {
        "backend": backend,
        "chunks": len(chunks),
        "documents": len({c.doc_id for c in chunks}),
        "embed_model": settings.embed_model,
        "config_profile": settings.config_profile,
        "path": str(target),
    }
