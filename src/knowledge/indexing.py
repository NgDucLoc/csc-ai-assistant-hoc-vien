"""Knowledge Indexing — Index (slide 39 Embed → Index; slide 34 bước 6 Serve).

Chỉ mục JSON là định dạng chính vì nó commit được vào repo, nên chạy ngay trên máy chưa dựng lại
được. Chroma là tùy chọn khi đã cài. Bản JSON luôn được ghi song song và là thứ ``retrieval`` đọc.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.config import settings
from src.knowledge.embedding import embed_chunks
from src.knowledge.preparation import build_chunks


def find_index(index_path: str | Path | None = None) -> Path | None:
    """Tìm tệp ``index.json``. Mặc định thử chỉ mục tự dựng trước, rồi tới bản dựng sẵn."""
    candidates = (
        [Path(index_path)]
        if index_path
        else [settings.abs_path(settings.chroma_path), settings.abs_path("data/index_prebuilt")]
    )
    for cand in candidates:
        f = cand / "index.json" if cand.is_dir() else cand
        if f.exists():
            return f
    return None


def read_index(path: Path) -> dict[str, Any]:
    """Đọc chỉ mục JSON: siêu dữ liệu dựng và danh sách đoạn kèm vector."""
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return payload


def _chroma_collection(path: Path, *, reset: bool = False) -> Any:
    import chromadb  # nhập muộn: chỉ cần khi dựng chỉ mục

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
    """Dựng chỉ mục vector từ kho tri thức: Chunk → Embed → Index.

    Mất vài phút trên CPU. Sửa bất kỳ tài liệu nào trong ``data/knowledge/`` thì phải dựng lại chỉ
    mục trong cùng một PR: chỉ mục lệch với kho là lỗi im lặng, truy hồi vẫn trả kết quả nhưng là
    kết quả sai.

    Returns:
        Bản tóm tắt số đoạn, số tài liệu và cấu hình đã dùng.
    """
    from src.llm.client import get_client

    target = Path(out_path) if out_path else settings.abs_path(settings.chroma_path)
    target.mkdir(parents=True, exist_ok=True)
    chunks = build_chunks()
    client = get_client()

    def progress(done: int, total: int) -> None:
        if verbose:
            print(f"  đã nhúng {done}/{total} đoạn")

    vectors = embed_chunks(chunks, client, batch_size=settings.embed_batch_size, on_progress=progress)

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
