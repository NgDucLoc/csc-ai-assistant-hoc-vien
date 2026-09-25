"""Kiểm tra môi trường học viên — Lab 0.

Chạy:
    uv run python scripts/check_env.py            # cấu hình chuẩn trong .env
    uv run python scripts/check_env.py --profile S
    uv run python scripts/check_env.py --profile L

**Mỗi hạng mục FAIL bắt buộc kèm hướng dẫn khắc phục cụ thể ngay trong kết
quả.** Học viên chạy bước này tại nhà, không có giảng viên bên cạnh để hỏi.
Một dòng "FAIL: không kết nối được" mà không nói phải làm gì tiếp theo là một
dòng vô dụng.

Kiểm cả ngân sách ổ đĩa, vì máy học viên không được reset giữa ba ngày học:
tới chiều ngày 3 nó mang model đã tải, ảnh Docker, chỉ mục, mlruns và cache.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MIN_FREE_GB = 10
MIN_PYTHON = (3, 11)


@dataclass
class Check:
    """Kết quả một hạng mục kiểm tra."""

    name: str
    ok: bool
    detail: str
    fix: str = ""


def _run(cmd: list[str], timeout: int = 20) -> tuple[bool, str]:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        text = (out.stdout or out.stderr).strip()
        return out.returncode == 0, text.splitlines()[0] if text else ""
    except FileNotFoundError:
        return False, "không tìm thấy lệnh"
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)


# --- phần chung ------------------------------------------------------------
def check_python() -> Check:
    """Phiên bản Python."""
    v = sys.version_info
    ok = (v.major, v.minor) >= MIN_PYTHON
    return Check(
        "Python >= 3.11",
        ok,
        f"đang dùng {v.major}.{v.minor}.{v.micro}",
        fix="Cài Python 3.11 rồi chạy lại: uv python install 3.11 && uv sync",
    )


def check_uv() -> Check:
    """Công cụ quản lý môi trường uv."""
    ok, detail = _run(["uv", "--version"])
    return Check(
        "uv đã cài",
        ok,
        detail,
        fix="macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh\n"
        '     Windows:     powershell -c "irm https://astral.sh/uv/install.ps1 | iex"',
    )


def check_lockfile() -> Check:
    """Khóa phụ thuộc đã được đồng bộ."""
    lock = ROOT / "uv.lock"
    venv = ROOT / ".venv"
    ok = lock.exists() and venv.exists()
    return Check(
        "Môi trường dựng bằng uv.lock",
        ok,
        f"uv.lock={'có' if lock.exists() else 'thiếu'}, .venv={'có' if venv.exists() else 'thiếu'}",
        fix="Chạy: uv sync\n" "     Nếu thiếu uv.lock, kéo lại từ nhánh main — tệp này BẮT BUỘC được commit.",
    )


def check_git() -> Check:
    """Git khả dụng."""
    ok, detail = _run(["git", "--version"])
    return Check("Git đã cài", ok, detail, fix="Cài Git từ https://git-scm.com/downloads")


def check_precommit() -> Check:
    """pre-commit đã gắn vào Git."""
    hook = ROOT / ".git" / "hooks" / "pre-commit"
    ok = hook.exists()
    return Check(
        "pre-commit đã gắn vào Git",
        ok,
        "hook có mặt" if ok else "chưa gắn hook",
        fix="Chạy: uv run pre-commit install\n"
        "     Hook này chặn commit chứa dữ liệu nhạy cảm — SPEC-DATA-01.",
    )


def check_docker() -> Check:
    """Docker khả dụng. Cần cho Lab 5."""
    ok, detail = _run(["docker", "--version"])
    return Check(
        "Docker khả dụng",
        ok,
        detail,
        fix="Cài Docker Desktop. Nếu Docker lỗi trên Windows, vẫn học được Lab 5 bằng\n"
        "     cách chạy trực tiếp các dịch vụ; phần đóng gói được chấm qua tệp cấu hình.",
    )


def check_disk() -> Check:
    """Ngân sách ổ đĩa cho ba ngày học."""
    free_gb = shutil.disk_usage(ROOT).free / (1024**3)
    ok = free_gb >= MIN_FREE_GB
    return Check(
        f"Ổ đĩa trống >= {MIN_FREE_GB} GB",
        ok,
        f"còn {free_gb:.1f} GB",
        fix="Máy không được reset giữa ba ngày học. Tới chiều ngày 3 nó chứa model,\n"
        "     ảnh Docker, chỉ mục, mlruns và cache. Dọn bớt trước khi vào lớp.",
    )


def check_data() -> Check:
    """Bộ dữ liệu và kho tri thức đầy đủ."""
    try:
        from src.data import load_adversarial, load_gold_qa, load_train
        from src.knowledge.governance import load_documents

        n_train = len(load_train())
        n_docs = len(load_documents(include_superseded=True))
        n_qa = len(load_gold_qa())
        n_adv = len(load_adversarial())
        ok = n_train == 80 and n_docs == 28 and n_qa == 45 and n_adv == 12
        detail = f"{n_train} ticket, {n_docs} tài liệu, {n_qa} câu hỏi vàng, {n_adv} ca đối kháng"
    except Exception as exc:  # noqa: BLE001
        return Check(
            "Bộ dữ liệu đầy đủ",
            False,
            str(exc),
            fix="Kéo lại nhánh main. Nếu vẫn lỗi, chạy: uv run python scripts/validate_data.py",
        )
    return Check(
        "Bộ dữ liệu đầy đủ", ok, detail, fix="Chạy: uv run python scripts/validate_data.py để biết thiếu gì."
    )


def check_retrieval() -> Check:
    """Truy hồi chạy được, kể cả khi chưa có chỉ mục vector."""
    try:
        from src.retrieval.pipeline import Retriever

        r = Retriever()
        hits = r.search("phí chậm nộp cước")
        ok = bool(hits)
        detail = f"{len(r.chunks)} đoạn, nhúng bằng {r.embed_model}"
    except Exception as exc:  # noqa: BLE001
        return Check(
            "Truy hồi tri thức",
            False,
            str(exc),
            fix="Chạy: uv run python scripts/build_index.py\n"
            "     Hoặc dùng bản dựng sẵn ở data/index_prebuilt/.",
        )
    return Check("Truy hồi tri thức", ok, detail, fix="Kiểm tra data/knowledge/ có đủ 28 tệp .md.")


# --- phần riêng theo cấu hình ---------------------------------------------
def check_llm_endpoint(profile: str) -> list[Check]:
    """Kết nối tới máy chủ suy luận và thử một lần sinh + một lần nhúng."""
    from src.config import settings
    from src.llm.client import LLMClient

    checks: list[Check] = []
    fix_s = (
        "Cấu hình S: kiểm tra LLM_API_KEY trong .env đúng khóa giảng viên cấp,\n"
        "     và máy có vào được mạng lớp học. Thử: curl $LLM_BASE_URL/models"
    )
    fix_l = (
        "Cấu hình L: khởi động Ollama rồi tải model:\n"
        "       ollama serve\n"
        "       ollama pull qwen3:8b\n"
        "       ollama pull bge-m3"
    )
    fix = fix_s if profile == "S" else fix_l

    try:
        client = LLMClient()
        resp = client.complete(
            task="classify",
            system="Bạn trả về đúng một từ.",
            user="Trả lời đúng một từ: OK",
        )
        src = "từ cache" if resp.from_cache else "gọi thật"
        checks.append(
            Check(f"Sinh văn bản ({settings.llm_model})", True, f"phản hồi {len(resp.text)} ký tự, {src}")
        )
    except Exception as exc:  # noqa: BLE001
        checks.append(Check(f"Sinh văn bản ({settings.llm_model})", False, str(exc)[:120], fix=fix))

    try:
        vectors = LLMClient().embed(["kiểm tra đường chạy nhúng"])
        dim = len(vectors[0]) if vectors else 0
        ok = dim > 0
        checks.append(
            Check(
                f"Tạo embedding ({settings.embed_model})",
                ok,
                f"{dim} chiều",
                fix="Model embedding phải là bge-m3 ở CẢ HAI cấu hình — SPEC-INFRA-01.\n"
                "     Dùng model khác sẽ gây lệch số chiều vector giữa các buổi.",
            )
        )
    except Exception as exc:  # noqa: BLE001
        checks.append(Check(f"Tạo embedding ({settings.embed_model})", False, str(exc)[:120], fix=fix))

    return checks


def main() -> int:
    """Chạy toàn bộ kiểm tra và in bảng PASS/FAIL."""
    ap = argparse.ArgumentParser(description="Kiểm tra môi trường học viên")
    ap.add_argument(
        "--profile",
        choices=["S", "L"],
        default=None,
        help="Ép một cấu hình. Bỏ trống thì dùng CONFIG_PROFILE trong .env",
    )
    ap.add_argument("--skip-llm", action="store_true", help="Bỏ qua phần cần máy chủ suy luận")
    args = ap.parse_args()

    import os

    if args.profile:
        os.environ["CONFIG_PROFILE"] = args.profile

    from src.config import settings

    profile = settings.config_profile
    print(f"KIỂM TRA MÔI TRƯỜNG — cấu hình {profile}")
    print(f"{settings.profile_banner()}\n")

    checks = [
        check_python(),
        check_uv(),
        check_lockfile(),
        check_git(),
        check_precommit(),
        check_docker(),
        check_disk(),
        check_data(),
        check_retrieval(),
    ]
    if not args.skip_llm:
        checks.extend(check_llm_endpoint(profile))

    width = max(len(c.name) for c in checks)
    failed: list[Check] = []
    for c in checks:
        mark = "PASS" if c.ok else "FAIL"
        print(f"  [{mark}]  {c.name:<{width}}  {c.detail}")
        if not c.ok:
            failed.append(c)

    print()
    if not failed:
        print(f"TẤT CẢ ĐẠT — môi trường sẵn sàng cho cấu hình {profile}.")
        print("Chụp màn hình kết quả này và nộp theo hướng dẫn Lab 0.")
        return 0

    print(f"CÓ {len(failed)} HẠNG MỤC CHƯA ĐẠT. Cách khắc phục:\n")
    for c in failed:
        print(f"  ▸ {c.name}")
        for line in (c.fix or "Liên hệ giảng viên.").splitlines():
            print(f"    {line}")
        print()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
