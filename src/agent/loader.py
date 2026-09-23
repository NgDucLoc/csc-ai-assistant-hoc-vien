"""Nạp prompt từ tệp và ép cấu trúc năm phần — SPEC-PROMPT-01, SPEC-PROMPT-02.

Mọi prompt phải có đủ năm phần: VAI TRÒ, NHIỆM VỤ, RÀNG BUỘC, NGỮ CẢNH,
ĐỊNH DẠNG ĐẦU RA. Ràng buộc này được ép bằng kiểm thử chứ không bằng lời nhắc,
vì prompt thiếu phần ràng buộc là nguyên nhân phổ biến nhất khiến model nhỏ
trả về đầu ra không dùng được.

Ngân sách prompt hệ thống (800 token theo SPEC-INFRA-04) cũng được ép ở đây.
Khi hạ tầng đủ nhanh, kỷ luật tối ưu ngữ cảnh chỉ còn giữ được bằng cổng kiểm
tra tự động — tốc độ phần cứng không còn ép giúp nữa.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.config import ROOT, settings
from src.knowledge.loader import parse_front_matter

PROMPT_DIR = ROOT / "src" / "agent" / "prompts"

REQUIRED_SECTIONS = ("VAI TRÒ", "NHIỆM VỤ", "RÀNG BUỘC", "NGỮ CẢNH", "ĐỊNH DẠNG ĐẦU RA")

_SECTION = re.compile(r"^#\s+(.+)$", re.MULTILINE)


@dataclass
class Prompt:
    """Một prompt đã nạp, kèm siêu dữ liệu phiên bản."""

    prompt_id: str
    version: int
    task: str
    template: str
    path: Path

    @property
    def ref(self) -> str:
        """Định danh dùng trong nhật ký, ví dụ ``classify.v2``."""
        return f"{self.prompt_id}.v{self.version}"

    def sections(self) -> list[str]:
        """Danh sách tiêu đề cấp 1 có trong prompt."""
        return [m.group(1).strip() for m in _SECTION.finditer(self.template)]

    def render(self, **values: Any) -> str:
        """Điền các chỗ trống trong mẫu.

        Dùng thay thế chuỗi trực tiếp thay vì ``str.format`` vì prompt chứa
        nhiều dấu ngoặc nhọn của ví dụ JSON, và ``str.format`` sẽ hiểu nhầm
        chúng là chỗ trống rồi ném lỗi khó truy nguyên.
        """
        out = self.template
        for key, value in values.items():
            out = out.replace("{" + key + "}", str(value))
        return out

    def estimated_tokens(self) -> int:
        """Ước lượng số token của mẫu.

        Dùng hệ số 3.2 ký tự mỗi token cho tiếng Việt — đủ chính xác để làm
        cổng chặn, và không kéo theo phụ thuộc vào một bộ tokenizer cụ thể.
        """
        return int(len(self.template) / 3.2)


def validate_structure(prompt: Prompt) -> list[str]:
    """Kiểm tra prompt có đủ năm phần bắt buộc và nằm trong ngân sách token.

    Returns:
        Danh sách lỗi. Rỗng nghĩa là hợp lệ.
    """
    problems: list[str] = []
    have = {s.upper() for s in prompt.sections()}
    for required in REQUIRED_SECTIONS:
        if required not in have:
            problems.append(f"{prompt.ref}: thiếu phần '{required}' (SPEC-PROMPT-01)")
    tokens = prompt.estimated_tokens()
    if tokens > settings.max_system_prompt_tokens:
        problems.append(
            f"{prompt.ref}: ước lượng {tokens} token, vượt ngân sách "
            f"{settings.max_system_prompt_tokens} (SPEC-INFRA-04)"
        )
    return problems


@lru_cache(maxsize=32)
def load_prompt(prompt_id: str, version: int | None = None) -> Prompt:
    """Nạp một prompt theo mã và phiên bản.

    Args:
        prompt_id: Ví dụ ``classify``.
        version: Số phiên bản. Bỏ trống thì lấy phiên bản cao nhất.

    Returns:
        Đối tượng ``Prompt``.

    Raises:
        FileNotFoundError: Không có tệp nào khớp.
    """
    candidates = sorted(PROMPT_DIR.glob(f"{prompt_id}.v*.md"))
    if not candidates:
        raise FileNotFoundError(f"Không tìm thấy prompt '{prompt_id}' trong {PROMPT_DIR}")

    if version is None:
        path = max(candidates, key=lambda p: int(p.stem.split(".v")[-1]))
    else:
        path = PROMPT_DIR / f"{prompt_id}.v{version}.md"
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy {path.name}")

    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    return Prompt(
        prompt_id=str(meta["prompt_id"]),
        version=int(str(meta["version"])),
        task=str(meta.get("task", prompt_id)),
        template=body.strip(),
        path=path,
    )


def list_prompts() -> list[Prompt]:
    """Nạp toàn bộ prompt trong kho, dùng cho kiểm thử và cho báo cáo."""
    out: list[Prompt] = []
    for path in sorted(PROMPT_DIR.glob("*.v*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        out.append(
            Prompt(
                prompt_id=str(meta["prompt_id"]),
                version=int(str(meta["version"])),
                task=str(meta.get("task", meta["prompt_id"])),
                template=body.strip(),
                path=path,
            )
        )
    return out
