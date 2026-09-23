"""Năm nhóm chỉ số bắt buộc — SPEC-EVAL-01.

1. **Phân loại**: accuracy, macro-F1, ma trận nhầm lẫn.
2. **Truy hồi**: Recall@k, MRR, và tỉ lệ từ chối đúng trên câu không có đáp án.
3. **Sinh văn bản**: tỉ lệ có trích dẫn hợp lệ, tỉ lệ trích dẫn bịa.
4. **Vận hành**: độ trễ p50/p95, số lời gọi model, tỉ lệ trúng cache.
5. **An toàn**: tỉ lệ chuyển người đúng, kết quả bộ ca đối kháng.

Ma trận nhầm lẫn được tính đầy đủ chứ không chỉ tổng hợp, vì phần phân tích
lỗi ở Session 5 dựa vào nó: cặp ``cuoc_thanh_toan`` với ``goi_cuoc_khuyen_mai``
sẽ hiện lên rõ, và kết luận cần rút ra là **đôi khi vấn đề nằm ở định nghĩa
nhãn chứ không nằm ở model.**
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import Any

CATEGORIES = [
    "cuoc_thanh_toan",
    "chat_luong_ket_noi",
    "goi_cuoc_khuyen_mai",
    "thiet_bi_sim",
    "thong_tin_thue_bao",
    "khac",
]


# --- 1. phân loại ----------------------------------------------------------
def confusion_matrix(truth: Sequence[str], pred: Sequence[str]) -> dict[str, dict[str, int]]:
    """Ma trận nhầm lẫn dạng ``{nhãn thật: {nhãn dự đoán: số ca}}``."""
    matrix: dict[str, dict[str, int]] = {t: dict.fromkeys(CATEGORIES, 0) for t in CATEGORIES}
    for t, p in zip(truth, pred, strict=True):
        if t in matrix:
            matrix[t][p if p in CATEGORIES else "khac"] += 1
    return matrix


def classification_metrics(truth: Sequence[str], pred: Sequence[str]) -> dict[str, Any]:
    """Accuracy, precision/recall/F1 theo lớp, và macro-F1."""
    # TODO(LAB-5): Accuracy, precision/recall/F1 theo lớp, và macro-F1
    #   Chạy "uv run pytest -m lab5" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-5: Accuracy, precision/recall/F1 theo lớp, và macro-F1")


def top_confusions(matrix: dict[str, dict[str, int]], limit: int = 3) -> list[dict[str, Any]]:
    """Các cặp bị nhầm nhiều nhất, dùng cho phần phân tích lỗi."""
    pairs: list[dict[str, Any]] = []
    for truth, row in matrix.items():
        for pred, count in row.items():
            if truth != pred and count:
                pairs.append({"truth": truth, "pred": pred, "count": count})
    return sorted(pairs, key=lambda p: p["count"], reverse=True)[:limit]


# --- 2. truy hồi -----------------------------------------------------------
def retrieval_metrics(results: Sequence[dict[str, Any]], k: int = 5) -> dict[str, Any]:
    """Recall@k, MRR, và tỉ lệ từ chối đúng.

    Args:
        results: Mỗi phần tử gồm ``expected`` (danh sách doc_id đúng),
            ``retrieved`` (danh sách doc_id đã truy hồi, theo thứ tự) và
            ``grounded`` (hệ thống có coi là đủ căn cứ không).
        k: Ngưỡng cắt.

    Returns:
        Bộ chỉ số truy hồi. ``refusal_accuracy`` đo riêng trên các câu không
        có đáp án — chỉ số này quan trọng ngang Recall, vì một trợ lý bịa ra
        chính sách gây rủi ro lớn hơn nhiều một trợ lý im lặng.
    """
    # TODO(LAB-5): Recall@k, MRR, và tỉ lệ từ chối đúng trên câu không có đáp án
    #   Chạy "uv run pytest -m lab5" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-5: Recall@k, MRR, và tỉ lệ từ chối đúng trên câu không có đáp án")


# --- 3. sinh văn bản -------------------------------------------------------
def generation_metrics(drafts: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Chất lượng dự thảo: trích dẫn hợp lệ và trích dẫn bịa."""
    produced = [d for d in drafts if (d.get("text") or "").strip()]
    if not produced:
        return {"drafts": 0, "valid_citation_rate": None, "hallucinated_citation_rate": None}

    with_citation = sum(1 for d in produced if d.get("citations"))
    hallucinated = sum(1 for d in produced if d.get("invalid_citations"))
    lengths = [len((d.get("text") or "").split()) for d in produced]

    return {
        "drafts": len(produced),
        "valid_citation_rate": round(with_citation / len(produced), 4),
        "hallucinated_citation_rate": round(hallucinated / len(produced), 4),
        "median_words": int(statistics.median(lengths)) if lengths else 0,
    }


# --- 4. vận hành -----------------------------------------------------------
def operational_metrics(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Độ trễ, ngân sách gọi model và tỉ lệ trúng cache."""
    latencies = sorted(r.get("total_ms", 0) for r in rows)
    if not latencies:
        return {"p50_ms": None, "p95_ms": None}

    def pct(p: float) -> int:
        idx = min(len(latencies) - 1, int(round(p * (len(latencies) - 1))))
        return latencies[idx]

    calls = [r.get("llm_calls", 0) for r in rows]
    return {
        "tickets": len(rows),
        "p50_ms": pct(0.50),
        "p95_ms": pct(0.95),
        "max_ms": latencies[-1],
        "mean_llm_calls": round(sum(calls) / len(calls), 2) if calls else 0,
        "max_llm_calls": max(calls) if calls else 0,
        "tickets_per_hour": round(3_600_000 / (sum(latencies) / len(latencies)), 1) if latencies else None,
    }


# --- 5. an toàn ------------------------------------------------------------
def safety_metrics(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Tỉ lệ chuyển người đúng và phân bố lý do chuyển.

    ``escalation_recall`` là chỉ số quan trọng nhất trong nhóm này: trên các ca
    mà nhãn nói phải chuyển người, hệ thống chuyển đúng bao nhiêu phần trăm.
    Bỏ sót một ca cần chuyển nguy hiểm hơn nhiều so với chuyển thừa.
    """
    # TODO(LAB-5): Tỉ lệ chuyển người đúng — bỏ sót nguy hiểm hơn chuyển thừa
    #   Chạy "uv run pytest -m lab5" để biết mình đã đúng chưa.
    raise NotImplementedError("LAB-5: Tỉ lệ chuyển người đúng — bỏ sót nguy hiểm hơn chuyển thừa")


def adversarial_metrics(results: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Kết quả bộ 12 ca đối kháng. Ngưỡng đạt là 12/12."""
    passed = [r for r in results if r.get("passed")]
    by_kind: dict[str, list[str]] = defaultdict(list)
    for row in results:
        if not row.get("passed"):
            by_kind[row.get("kind", "?")].append(row.get("case_id", "?"))
    return {
        "total": len(results),
        "passed": len(passed),
        "pass_rate": round(len(passed) / len(results), 4) if results else None,
        "failures_by_kind": dict(by_kind),
    }
