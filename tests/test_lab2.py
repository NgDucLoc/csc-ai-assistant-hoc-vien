"""Lab 2 — kiến trúc, cấu hình hai đường chạy, ADR.

Bài kiểm thử quan trọng nhất tệp này là ``test_no_llm_call_outside_client``.
Nó quét mã nguồn để ép ràng buộc SPEC-ARCH-02: không lời gọi model nào nằm
ngoài ``src/llm/client.py``.

Ràng buộc đó không phải thẩm mỹ kiến trúc. Cache, ghi nhật ký, đếm ngân sách
và ngắt mạch chỉ hoạt động đồng nhất khi mọi lời gọi đi qua cùng một cửa. Một
lời gọi lọt ra ngoài là một lỗ hổng không được cache, không được ghi log, và
không được ngắt mạch — và nó sẽ chỉ lộ ra vào lúc hệ thống đang chịu tải.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.config import ROOT, TASK_PARAMS, Settings

pytestmark = pytest.mark.lab2

ALLOWED = {ROOT / "src" / "llm" / "client.py"}

# Dấu hiệu của một lời gọi model trực tiếp.
FORBIDDEN = [
    re.compile(r"chat/completions"),
    re.compile(r"\bopenai\b"),
    re.compile(r"/v1/embeddings"),
    re.compile(r"\.post\(\s*f?['\"]?\{?settings\.llm_base_url"),
]


def _source_files() -> list[Path]:
    return [p for p in (ROOT / "src").rglob("*.py") if p not in ALLOWED]


def test_no_llm_call_outside_client() -> None:
    """SPEC-ARCH-02 mục 2 — mọi lời gọi model phải đi qua src/llm/client.py."""
    offenders: list[str] = []
    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                offenders.append(f"{path.relative_to(ROOT)} khớp {pattern.pattern!r}")
    assert not offenders, "Phát hiện lời gọi model ngoài src/llm/client.py:\n  " + "\n  ".join(offenders)


def test_profile_switch_needs_no_code_change(monkeypatch: pytest.MonkeyPatch) -> None:
    """SPEC-INFRA-07 — chuyển S↔L chỉ bằng biến môi trường."""
    monkeypatch.setenv("CONFIG_PROFILE", "S")
    monkeypatch.setenv("LLM_BASE_URL", "http://server:4000/v1")
    monkeypatch.setenv("LLM_MODEL", "Qwen3-8B")
    s = Settings()
    assert s.config_profile == "S"
    assert s.llm_model == "Qwen3-8B"

    monkeypatch.setenv("CONFIG_PROFILE", "L")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LLM_MODEL", "qwen3:8b")
    s = Settings()
    assert s.config_profile == "L"
    assert s.llm_model == "qwen3:8b"


def test_embedding_model_is_identical_across_profiles(monkeypatch: pytest.MonkeyPatch) -> None:
    """SPEC-INFRA-01 — model embedding giống nhau ở cả hai cấu hình.

    Nếu để hai model embedding khác nhau, chỉ mục dựng ở cấu hình này không đọc
    được ở cấu hình kia, và học viên mất rất nhiều thời gian truy nguyên một
    lỗi sai lệch số chiều vector giữa hai buổi học.
    """
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    embed_lines = [ln for ln in example.splitlines() if ln.strip().lstrip("# ").startswith("EMBED_MODEL=")]
    models = {ln.split("=", 1)[1].strip() for ln in embed_lines}
    assert models == {"bge-m3"}, f"Model embedding phải giống nhau ở cả hai cấu hình, thấy: {models}"


def test_cache_key_includes_base_url_and_model() -> None:
    """SPEC-LLM-02 — khóa cache phải phân biệt được hai cấu hình."""
    from src.llm.cache import make_key

    common = {
        "task": "classify",
        "messages": [{"role": "user", "content": "x"}],
        "params": {"temperature": 0},
    }
    a = make_key(base_url="http://a/v1", model="m1", **common)
    b = make_key(base_url="http://b/v1", model="m1", **common)
    c = make_key(base_url="http://a/v1", model="m2", **common)
    assert a != b, "Đổi base_url phải cho khóa cache khác"
    assert a != c, "Đổi tên model phải cho khóa cache khác"


def test_classification_is_deterministic_by_config() -> None:
    """SPEC-LLM-03 — phân loại chạy ở nhiệt độ 0, sinh phản hồi thì không.

    Kết luận này đến từ thí nghiệm ở Session 2 bước 2 và là lý do hệ thống
    không dùng chung một cấu hình model cho mọi bước.
    """
    assert TASK_PARAMS["classify"]["temperature"] == 0.0
    assert TASK_PARAMS["extract"]["temperature"] == 0.0
    assert TASK_PARAMS["generate"]["temperature"] > 0.0


def test_adr_files_follow_four_part_template() -> None:
    """SPEC-TOOLING-05 — tối thiểu 5 ADR, mỗi ADR đủ bốn phần.

    Một ADR không nêu được phương án đã cân nhắc thì không phải ADR, và không
    dùng để bảo vệ quyết định thiết kế ở Session 6 được.
    """
    adr_dir = ROOT / "docs" / "adr"
    files = sorted(p for p in adr_dir.glob("*.md") if not p.name.startswith("0000"))
    assert len(files) >= 5, f"Cần tối thiểu 5 ADR, đang có {len(files)}"

    required = ["## Bối cảnh", "## Các phương án đã cân nhắc", "## Quyết định", "## Hệ quả chấp nhận"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        missing = [part for part in required if part not in text]
        assert not missing, f"{path.name}: thiếu phần {missing}"


def test_repo_structure_matches_spec() -> None:
    """SPEC-ARCH-03 — các thư mục và tệp bắt buộc đều có mặt."""
    required = [
        "src/config.py",
        "src/llm/client.py",
        "src/llm/cache.py",
        "src/llm/schema.py",
        "src/knowledge/sourcing.py",
        "src/knowledge/governance.py",
        "src/knowledge/preparation.py",
        "src/knowledge/embedding.py",
        "src/knowledge/indexing.py",
        "src/retrieval/transform.py",
        "src/retrieval/search.py",
        "src/retrieval/filters.py",
        "src/retrieval/rerank.py",
        "src/retrieval/pipeline.py",
        "src/context/assemble.py",
        "src/agent/tools.py",
        "src/agent/workflow.py",
        "src/agent/generator.py",
        "src/guardrails/input_rules.py",
        "src/guardrails/output_rules.py",
        "src/api/main.py",
        "src/ui/app.py",
        "eval/run_eval.py",
        "eval/metrics.py",
        "pyproject.toml",
        ".env.example",
        ".pre-commit-config.yaml",
        "models/Modelfile",
        "docker-compose.yml",
        ".github/workflows/ci.yml",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    assert not missing, f"Thiếu các thành phần bắt buộc theo SPEC-ARCH-03: {missing}"
