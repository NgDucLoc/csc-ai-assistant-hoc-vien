"""Công cụ đo cho Lab 3 — chạy được ngay sau khi viết xong từng khối, không cần Lab 4 và Lab 5.

Chạy: uv run python scripts/lab3_check.py <chế độ> [tùy chọn]

Mỗi chế độ ứng với một chặng của pipeline tri thức (slide 34 và slide 39):

* ``ingest``    — Discover, Ingest, Govern: bao nhiêu tài liệu, bản nào còn hiệu lực.
* ``chunks``    — Prepare: xem tài liệu được chia đoạn ra sao.
* ``embed``     — Embed: nhúng một vài đoạn, xem vector và thử tìm theo nghĩa.
* ``retrieval`` — Retrieve, Filter: đo Recall@5, MRR, tỉ lệ từ chối đúng; quét ngưỡng.
* ``context``   — Context: xem khối ngữ cảnh ghép cho một câu hỏi và ngân sách token.
* ``ask``       — Cả pipeline: truy hồi, ghép context, nhờ model trả lời có trích dẫn.
* ``layers``    — Bốn lớp phòng vệ đầu ra và ``classify`` (dùng model).

Vì sao có tệp này: ``eval/run_eval.py`` chạy toàn bộ quy trình xử lý ticket và các hàm chỉ số, mà hai
thứ đó chỉ được viết ở Lab 4 và Lab 5. Ở Lab 3, tệp này là cách đo chạy được.

Tệp này dùng đúng các khối do nhóm viết (``chunk_document``, ``embed_chunks``, ``hybrid_search``,
``judge_evidence``, ``assemble_context``, ``classify``). Khối nào chưa viết thì báo rõ.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings  # noqa: E402
from src.data import load_gold_qa, load_train  # noqa: E402

RAG_TOP_K = 5
CHARS_PER_TOKEN = 3.2  # cùng hệ số với bài kiểm thử ngân sách


def _not_written(exc: NotImplementedError) -> int:
    """In thông báo thân thiện khi một khối chưa được viết."""
    print(f"\nChưa chạy được: {exc}")
    print("Viết khối đó trước, rồi chạy lại. Kiểm tra bằng: uv run pytest -m lab3")
    return 2


def _no_model(exc: Exception, what: str = "model") -> int:
    print(f"\nKhông gọi được {what}: {exc}")
    print("Kiểm tra Ollama đang chạy chưa (ollama serve) và model đã tải chưa (ollama list).")
    return 1


def _pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.0f}%" if whole else "—"


def _set_setting(name: str, value: Any) -> None:
    """Đổi một tham số cấu hình trong tiến trình này (``Settings`` là dataclass đóng băng)."""
    object.__setattr__(settings, name, value)


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------
def run_ingest(doc_id: str | None) -> int:
    from src.knowledge.governance import conflict_report, load_documents
    from src.knowledge.sourcing import discover_documents, ingest_documents

    files = discover_documents()
    everything = ingest_documents()
    current = load_documents()
    print(f"Discover: {len(files)} tệp trong data/knowledge/")
    print(f"Ingest:   {len(everything)} tài liệu đọc được, đủ các trường bắt buộc")
    print(
        f"Govern:   {len(current)} tài liệu còn hiệu lực, {len(everything) - len(current)} đã bị thay thế\n"
    )

    print("Các cặp tài liệu cũ và mới (SPEC-DATA-05):")
    for p in conflict_report():
        print(
            f"  {p['old_doc']} v{p['old_version']} ({p['old_status']}) được thay bằng "
            f"{p['new_doc']} v{p['new_version']} (hiệu lực {p['new_effective']}): {p['title']}"
        )

    doc = next((d for d in everything if d.doc_id == doc_id), everything[0])
    print(f"\nSiêu dữ liệu của {doc.doc_id}:")
    for key in ("title", "category", "version", "effective_date", "status", "supersedes"):
        print(f"  {key:<15} {getattr(doc, key)}")
    print(f"  {'độ dài thân':<15} {len(doc.body)} ký tự")
    return 0


# ---------------------------------------------------------------------------
# chunks
# ---------------------------------------------------------------------------
def _all_chunks(chunk_size: int | None, overlap: int | None) -> list[Any]:
    from src.knowledge.governance import load_documents
    from src.knowledge.preparation import chunk_document

    out: list[Any] = []
    for doc in load_documents():
        out.extend(chunk_document(doc, max_chars=chunk_size, overlap=overlap))
    return out


def run_chunks(doc_id: str | None, chunk_size: int | None, overlap: int | None) -> int:
    chunks = _all_chunks(chunk_size, overlap)
    lens = [len(c.text) for c in chunks]
    size = chunk_size or settings.chunk_size
    print(
        f"{len(chunks)} đoạn từ {len({c.doc_id for c in chunks})} tài liệu · kích thước tối đa {size} ký tự"
    )
    print(f"Độ dài đoạn: nhỏ nhất {min(lens)}, trung bình {sum(lens) // len(lens)}, lớn nhất {max(lens)}\n")
    target = doc_id or chunks[0].doc_id
    print(f"Các đoạn của {target}:")
    for c in chunks:
        if c.doc_id != target:
            continue
        preview = c.text.replace("\n", " ")[:80]
        print(f"  {c.chunk_id:<10} {len(c.text):>4} ký tự · {c.section[:30]:<30} · {preview}…")
    return 0


# ---------------------------------------------------------------------------
# embed
# ---------------------------------------------------------------------------
def run_embed(sample: int, query: str) -> int:
    from src.knowledge.embedding import embed_chunks
    from src.llm.client import get_client
    from src.retrieval.search import cosine

    chunks = _all_chunks(None, None)[:sample]
    client = get_client()
    started = time.perf_counter()
    try:
        vectors = embed_chunks(chunks, client, batch_size=settings.embed_batch_size)
        qvec = client.embed([query])[0]
    except NotImplementedError:
        raise
    except Exception as exc:  # noqa: BLE001
        return _no_model(exc, f"model embedding {settings.embed_model}")

    print(
        f"Model embedding: {settings.embed_model} · {len(chunks)} đoạn "
        f"· {time.perf_counter() - started:.1f} giây"
    )
    print(f"Số chiều của mỗi vector: {len(vectors[0])}")
    print(f"10 số đầu của vector đoạn đầu tiên: {[round(x, 3) for x in vectors[0][:10]]}\n")
    print(f'Tìm theo nghĩa cho câu: "{query}" (xếp theo cosine với vector câu hỏi)')
    ranked = sorted(zip(chunks, vectors, strict=True), key=lambda p: cosine(qvec, p[1]), reverse=True)
    for c, v in ranked[:5]:
        print(f"  {cosine(qvec, v):.3f}  {c.chunk_id:<10} {c.doc_title} — {c.section}")
    return 0


# ---------------------------------------------------------------------------
# retrieval
# ---------------------------------------------------------------------------
def _build_retriever(args: argparse.Namespace) -> tuple[Any, str]:
    """Dựng Retriever theo nguồn đoạn. Trả về (retriever, mô tả)."""
    from src.knowledge.embedding import embed_chunks
    from src.llm.client import get_client
    from src.retrieval.pipeline import Retriever
    from src.retrieval.search import chunk_tokens, tokenize

    if args.source == "index":
        r = Retriever(args.index)
        where = f"chỉ mục có sẵn {r.path or '(chưa có, dùng từ khóa trong bộ nhớ)'}"
    else:
        r = Retriever("không-có-tệp-này")  # ép Retriever không nạp chỉ mục nào
        chunks = _all_chunks(args.chunk_size, args.overlap)
        r.chunks = [
            {
                "chunk_id": c.chunk_id,
                "doc_id": c.doc_id,
                "doc_title": c.doc_title,
                "section": c.section,
                "category": c.category,
                "version": c.version,
                "effective_date": c.effective_date,
                "text": c.text,
                "embedding": [],
            }
            for c in chunks
        ]
        where = (
            f"đoạn dựng từ chunk_document của nhóm (tối đa {args.chunk_size or settings.chunk_size} ký tự)"
        )
        if args.search != "keyword":
            vectors = embed_chunks(chunks, get_client(), batch_size=settings.embed_batch_size)
            for c, v in zip(r.chunks, vectors, strict=True):
                c["embedding"] = v
            where += f", đã nhúng bằng {settings.embed_model}"
    r.has_vectors = args.search != "keyword" and any(c.get("embedding") for c in r.chunks)
    for c in r.chunks:
        c.pop("_tokens", None)
        if args.no_title:
            c["_tokens"] = set(tokenize(c["text"]))
        else:
            chunk_tokens(c)
    return r, where


def _print_sweep(top_scores: list[tuple[bool, float]]) -> None:
    """Bảng đánh đổi giữa từ chối đúng và từ chối thừa khi đổi ngưỡng."""
    answerable = [s for ok, s in top_scores if ok]
    unanswerable = [s for ok, s in top_scores if not ok]
    print("\nQuét ngưỡng (điểm cao nhất dưới ngưỡng thì từ chối)")
    print(f"{'Ngưỡng':>7} {'Từ chối đúng':>14} {'Từ chối thừa':>14}")
    everything = answerable + unanswerable
    for i in range(max(1, int(min(everything) * 20)), int(max(everything) * 20) + 2):
        t = i * 0.05
        refused = sum(s < t for s in unanswerable)
        over = sum(s < t for s in answerable)
        print(
            f"{t:>7.2f} {refused / max(1, len(unanswerable)):>14.2f} {over / max(1, len(answerable)):>14.2f}"
        )
    print(
        f"Điểm cao nhất của câu có đáp án: từ {min(answerable):.2f} đến {max(answerable):.2f}. "
        f"Của câu không có đáp án: từ {min(unanswerable):.2f} đến {max(unanswerable):.2f}."
    )


def run_retrieval(args: argparse.Namespace) -> int:
    from src.knowledge.governance import load_documents
    from src.llm.client import get_client
    from src.retrieval.transform import rewrite_query

    if args.rerank:
        _set_setting("rerank_enabled", True)
    if args.vector_weight is not None:
        _set_setting("vector_weight", args.vector_weight)
    try:
        retriever, where = _build_retriever(args)
    except NotImplementedError:
        raise
    except Exception as exc:  # noqa: BLE001
        return _no_model(exc, f"model embedding {settings.embed_model}")

    rows = load_gold_qa()
    doc_category = {d.doc_id: d.category for d in load_documents()}
    client = get_client() if args.rewrite else None
    min_score = args.min_score if args.min_score is not None else settings.retrieve_min_score
    answerable = [r for r in rows if r.get("answerable", True)]
    unanswerable = [r for r in rows if not r.get("answerable", True)]

    hits_at_k = 0
    rr_sum = 0.0
    refused_ok = 0
    over_refused = 0
    misses: list[str] = []
    bad_grounded: list[str] = []
    top_scores: list[tuple[bool, float]] = []
    modes: set[str] = set()
    try:
        for row in rows:
            query = row["question"]
            if client:
                client.reset_budget()
            expected_ids = row.get("expected_doc_ids") or []
            category = doc_category.get(expected_ids[0], "khac") if expected_ids else "khac"
            rewritten = rewrite_query(query, category, client=client) if args.rewrite else None
            out = retriever.retrieve(query, top_k=args.top_k, min_score=min_score, rewritten=rewritten)
            modes.add(out.mode)
            ids = [h.doc_id for h in out.hits]
            top_scores.append((bool(row.get("answerable", True)), out.top_score))
            if row.get("answerable", True):
                expected = set(expected_ids)
                rank = next((i for i, d in enumerate(ids, 1) if d in expected), 0)
                hits_at_k += rank > 0
                rr_sum += 1 / rank if rank else 0.0
                over_refused += not out.grounded
                if not rank:
                    misses.append(
                        f"  {row['qa_id']}: cần {sorted(expected)}, tìm được {ids[:3]} "
                        f"(điểm cao nhất {out.top_score:.2f})"
                    )
            else:
                refused_ok += not out.grounded
                if out.grounded:
                    bad_grounded.append(
                        f"  {row['qa_id']}: điểm cao nhất {out.top_score:.2f} "
                        f"vượt ngưỡng {min_score:.2f}, hệ thống sẽ trả lời"
                    )
    except NotImplementedError:
        raise
    except Exception as exc:  # noqa: BLE001
        return _no_model(exc)

    print(f"Cấu hình: {settings.profile_banner()}")
    print(f"Nguồn đoạn: {where}")
    print(
        f"Chế độ tìm: {'/'.join(sorted(modes))} · viết lại truy vấn {'bật' if args.rewrite else 'tắt'} "
        f"· rerank {'bật' if args.rerank else 'tắt'} · tiêu đề {'tắt' if args.no_title else 'bật'} "
        f"· ngưỡng {min_score:.2f} · top-k {args.top_k}\n"
    )
    n = len(answerable)
    print(f"{'Chỉ số':<32} {'Giá trị':>8}   Ghi chú")
    print(
        f"{'Recall@5':<32} {hits_at_k / n:>8.3f}   "
        f"{hits_at_k}/{n} câu tìm thấy tài liệu đúng trong {args.top_k} kết quả đầu"
    )
    print(f"{'MRR':<32} {rr_sum / n:>8.3f}   tài liệu đúng nằm càng cao càng gần 1")
    print(
        f"{'Tỉ lệ từ chối đúng':<32} {refused_ok / max(1, len(unanswerable)):>8.3f}   "
        f"{refused_ok}/{len(unanswerable)} câu không có đáp án được từ chối"
    )
    print(
        f"{'Từ chối thừa':<32} {over_refused / n:>8.3f}   "
        f"{over_refused}/{n} câu có đáp án nhưng bị chuyển người"
    )
    if args.sweep:
        _print_sweep(top_scores)
    if args.show_failures:
        print("\nCâu không tìm thấy tài liệu đúng:")
        print("\n".join(misses) or "  (không có)")
        print("Câu không có đáp án nhưng hệ thống vẫn cho là đủ căn cứ (nguy cơ bịa):")
        print("\n".join(bad_grounded) or "  (không có)")
    return 0


# ---------------------------------------------------------------------------
# context và ask
# ---------------------------------------------------------------------------
def _retrieve_for(args: argparse.Namespace) -> Any:
    from src.retrieval.pipeline import Retriever

    retriever = Retriever(args.index)
    return retriever.retrieve(args.query, top_k=args.top_k, min_score=args.min_score)


def run_context(args: argparse.Namespace) -> int:
    from src.agent.loader import load_prompt

    result = _retrieve_for(args)
    block = result.context_block(max_chars=args.max_chars)
    print(f'Câu hỏi: "{args.query}"')
    print(
        f"Chế độ tìm: {result.mode} · {len(result.hits)} kết quả "
        f"· đủ căn cứ: {result.grounded} ({result.reason})\n"
    )
    for h in result.hits:
        print(f"  {h.score:.3f}  {h.chunk_id:<10} {h.doc_title} — {h.section}")
    print(f"\nKhối context ({len(block)} ký tự, ngân sách {args.max_chars}):\n")
    print(block or "(rỗng)")

    prompt_tokens = len(load_prompt("generate").template) / CHARS_PER_TOKEN
    ctx_tokens = len(block) / CHARS_PER_TOKEN
    print(
        f"\nƯớc lượng token: prompt sinh phản hồi {prompt_tokens:.0f} + context {ctx_tokens:.0f} "
        f"= {prompt_tokens + ctx_tokens:.0f} (trần cả lời gọi {settings.max_context_tokens})"
    )
    return 0


ASK_SYSTEM = (
    "Bạn là trợ lý hỗ trợ giao dịch viên chăm sóc khách hàng viễn thông. Chỉ dùng thông tin trong phần "
    "NGỮ CẢNH. Mỗi ý phải kèm trích dẫn nguyên văn dạng [KB-xxx vY, hiệu lực yyyy-mm-dd]. "
    "Nếu ngữ cảnh không đủ để trả lời, chỉ trả lời đúng chuỗi: KHÔNG ĐỦ CĂN CỨ."
)


def run_ask(args: argparse.Namespace) -> int:
    from src.llm.client import get_client

    result = _retrieve_for(args)
    print(f'Câu hỏi: "{args.query}"')
    print(f"Truy hồi ({result.mode}): điểm cao nhất {result.top_score:.3f}. {result.reason}")
    if not result.grounded:
        print("\nHệ thống KHÔNG gọi model: không đủ căn cứ, chuyển giao dịch viên (SPEC-RAG-03).")
        return 0
    block = result.context_block()
    user = f"NGỮ CẢNH:\n{block}\n\nCÂU HỎI CỦA KHÁCH: {args.query}\n\nTrả lời ngắn gọn, có trích dẫn."
    try:
        answer = get_client().complete(task="generate", system=ASK_SYSTEM, user=user).text
    except Exception as exc:  # noqa: BLE001
        return _no_model(exc)
    print("\nCác đoạn đã đưa cho model:")
    for h in result.hits:
        print(f"  {h.citation()} {h.doc_title} — {h.section}")
    print(f"\nTrả lời của model:\n{answer.strip()}")
    return 0


# ---------------------------------------------------------------------------
# layers
# ---------------------------------------------------------------------------
GOOD = {
    "category": "cuoc_thanh_toan",
    "priority": "P2",
    "sentiment": "buc_boi",
    "confidence": 0.85,
    "entities": {},
    "reason": "Khách bị trừ tiền.",
}
_GOOD_JSON = json.dumps(GOOD, ensure_ascii=False)

# (mô tả kiểu hỏng, đầu ra lần 1, đầu ra khi model được báo lỗi và sửa lại)
BAD_OUTPUTS: list[tuple[str, str, str]] = [
    ("Đúng ngay từ đầu", _GOOD_JSON, _GOOD_JSON),
    ("Bọc trong khối mã", "```json\n" + _GOOD_JSON + "\n```", _GOOD_JSON),
    ("Có lời dẫn phía trước", "Đây là kết quả phân loại:\n" + _GOOD_JSON, _GOOD_JSON),
    ("Dùng nháy đơn", str(GOOD), _GOOD_JSON),
    ("Sai giá trị enum", json.dumps({**GOOD, "category": "billing"}, ensure_ascii=False), _GOOD_JSON),
    ("Độ tin cậy ngoài [0, 1]", json.dumps({**GOOD, "confidence": 1.7}, ensure_ascii=False), _GOOD_JSON),
    (
        "Thiếu trường bắt buộc",
        json.dumps({k: v for k, v in GOOD.items() if k != "sentiment"}, ensure_ascii=False),
        _GOOD_JSON,
    ),
    ("Trả văn xuôi, không có JSON", "Ticket này nói về việc bị trừ tiền, nên xếp vào nhóm cước.", _GOOD_JSON),
]


def _layer1_only(raw: str, schema: dict[str, Any], validate: Callable[..., list[str]]) -> bool:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return False
    return isinstance(data, dict) and not validate(data, schema)


def _layers12(
    raw: str,
    schema: dict[str, Any],
    validate: Callable[..., list[str]],
    extract: Callable[[str], dict[str, Any] | None],
) -> bool:
    data = extract(raw)
    return data is not None and not validate(data, schema)


def run_layers(live: int) -> int:
    from src.llm.schema import (
        CLASSIFICATION_FALLBACK,
        CLASSIFICATION_SCHEMA,
        extract_json,
        parse_with_retry,
        validate,
    )

    print("Bốn lớp phòng vệ trên 8 kiểu đầu ra hỏng có sẵn (không gọi model)\n")
    print(f"{'Kiểu hỏng':<32} {'Lớp 1':>6} {'1+2':>6} {'1+2+3':>7}  Lớp cuối cùng cứu được")
    totals = {"l1": 0, "l12": 0, "l123": 0}
    mark = lambda ok: "đạt" if ok else "hỏng"  # noqa: E731
    for label, first, fixed in BAD_OUTPUTS:
        l1 = _layer1_only(first, CLASSIFICATION_SCHEMA, validate)
        l12 = _layers12(first, CLASSIFICATION_SCHEMA, validate, extract_json)

        def call(error: str | None, first: str = first, fixed: str = fixed) -> str:
            return fixed if error else first

        outcome = parse_with_retry(call, CLASSIFICATION_SCHEMA, CLASSIFICATION_FALLBACK)
        totals["l1"] += l1
        totals["l12"] += l12
        totals["l123"] += outcome.ok
        print(f"{label:<32} {mark(l1):>6} {mark(l12):>6} {mark(outcome.ok):>7}  {outcome.layer}")

    stuck = parse_with_retry(lambda _e: "không phải JSON", CLASSIFICATION_SCHEMA, CLASSIFICATION_FALLBACK)
    n = len(BAD_OUTPUTS)
    print(
        f"\nSố ca đạt: chỉ lớp 1 = {totals['l1']}/{n} · lớp 1+2 = {totals['l12']}/{n} "
        f"· lớp 1+2+3 = {totals['l123']}/{n}"
    )
    print(
        f"Model không bao giờ sửa được → lớp {stuck.layer}, needs_human = {stuck.data.get('needs_human')}, "
        f"thử {stuck.attempts} lần, không ném lỗi."
    )
    return _layers_live(live) if live else 0


def _layers_live(count: int) -> int:
    from src.agent.classifier import SYSTEM, classify
    from src.agent.loader import load_prompt
    from src.llm.client import get_client
    from src.llm.schema import CLASSIFICATION_SCHEMA, extract_json, schema_hint, validate

    tickets = load_train()[:count]
    client = get_client()
    prompt = load_prompt("classify")
    print(f"\nĐo trên {len(tickets)} ticket thật ({settings.profile_banner()})\n")

    only1 = plus2 = calls = correct = 0
    layers: dict[str, int] = {}
    started = time.perf_counter()
    try:
        for i, t in enumerate(tickets, 1):
            client.reset_budget()
            rendered = prompt.render(
                ticket_text=t["customer_msg"], schema_hint=schema_hint(CLASSIFICATION_SCHEMA)
            )
            raw = client.complete(task="classify", system=SYSTEM, user=rendered).text
            only1 += _layer1_only(raw, CLASSIFICATION_SCHEMA, validate)
            plus2 += _layers12(raw, CLASSIFICATION_SCHEMA, validate, extract_json)
            client.reset_budget()
            result = classify(t["customer_msg"], client=client)
            layers[result.defense_layer] = layers.get(result.defense_layer, 0) + 1
            calls += result.attempts
            correct += result.category == t["label"]["category"]
            print(f"  {i}/{len(tickets)} · lớp {result.defense_layer}", end="\r")
    except NotImplementedError:
        raise
    except Exception as exc:  # noqa: BLE001
        return _no_model(exc)

    n = len(tickets)
    fallback = layers.get("fallback", 0)
    print(f"\n{'Chỉ số':<44} {'Chỉ lớp 1':>10} {'Đủ 4 lớp':>10}")
    print(f"{'Tỉ lệ phân tích cú pháp thành công':<44} {_pct(only1, n):>10} {_pct(n - fallback, n):>10}")
    print(f"{'  (chỉ lớp 1 + 2, không thử lại)':<44} {_pct(plus2, n):>10} {'':>10}")
    print(f"{'Tỉ lệ phải dùng lớp dự phòng':<44} {'—':>10} {_pct(fallback, n):>10}")
    print(f"{'Số lần gọi model trung bình mỗi ticket':<44} {'1.00':>10} {calls / n:>10.2f}")
    print(f"\nPhân bố lớp đã cứu: {dict(sorted(layers.items()))}")
    print(f"Nhóm vấn đề đúng nhãn: {_pct(correct, n)} · thời gian {time.perf_counter() - started:.0f} giây")
    return 0


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Công cụ đo cho Lab 3")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest", help="Discover, Ingest, Govern")
    p.add_argument("--doc", default=None, help="Mã tài liệu, ví dụ KB-001")

    p = sub.add_parser("chunks", help="Xem cách chia đoạn")
    p.add_argument("--doc", default=None, help="Mã tài liệu, ví dụ KB-001")
    p.add_argument("--chunk-size", type=int, default=None)
    p.add_argument("--overlap", type=int, default=None)

    p = sub.add_parser("embed", help="Nhúng vài đoạn và thử tìm theo nghĩa")
    p.add_argument("--sample", type=int, default=20, help="Số đoạn đầu tiên đem nhúng")
    p.add_argument("--query", default="phí chậm nộp cước tính thế nào")

    p = sub.add_parser("retrieval", help="Đo chất lượng truy hồi")
    p.add_argument(
        "--source",
        choices=["memory", "index"],
        default="memory",
        help="memory: dựng đoạn bằng chunk_document của nhóm. index: dùng chỉ mục có sẵn",
    )
    p.add_argument("--index", default=None, help="Đường dẫn chỉ mục khi --source index")
    p.add_argument(
        "--search",
        choices=["keyword", "hybrid"],
        default="hybrid",
        help="keyword: chỉ từ khóa. hybrid: từ khóa cộng vector (cần model embedding)",
    )
    p.add_argument("--chunk-size", type=int, default=None)
    p.add_argument("--overlap", type=int, default=None)
    p.add_argument("--no-title", action="store_true", help="Bỏ tiêu đề tài liệu và mục khỏi phần từ khóa")
    p.add_argument("--rewrite", action="store_true", help="Viết lại truy vấn trước khi tìm (cần model)")
    p.add_argument("--rerank", action="store_true", help="Bật rerank")
    p.add_argument("--vector-weight", type=float, default=None, help="Trọng số vector trong hybrid")
    p.add_argument("--min-score", type=float, default=None)
    p.add_argument("--top-k", type=int, default=RAG_TOP_K)
    p.add_argument("--show-failures", action="store_true")
    p.add_argument("--sweep", action="store_true", help="Quét ngưỡng")

    for name, helptext in (("context", "Xem khối context cho một câu hỏi"), ("ask", "Hỏi cả pipeline")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("query", help="Câu hỏi của khách")
        p.add_argument("--index", default=None)
        p.add_argument("--top-k", type=int, default=RAG_TOP_K)
        p.add_argument("--min-score", type=float, default=None)
        p.add_argument("--max-chars", type=int, default=2000)

    p = sub.add_parser("layers", help="Bốn lớp phòng vệ và classify")
    p.add_argument("--live", type=int, default=0, help="Đo thêm trên N ticket thật (cần model)")

    args = ap.parse_args()
    handlers: dict[str, Callable[[], int]] = {
        "ingest": lambda: run_ingest(args.doc),
        "chunks": lambda: run_chunks(args.doc, args.chunk_size, args.overlap),
        "embed": lambda: run_embed(args.sample, args.query),
        "retrieval": lambda: run_retrieval(args),
        "context": lambda: run_context(args),
        "ask": lambda: run_ask(args),
        "layers": lambda: run_layers(args.live),
    }
    try:
        return handlers[args.command]()
    except NotImplementedError as exc:
        return _not_written(exc)


if __name__ == "__main__":
    raise SystemExit(main())
