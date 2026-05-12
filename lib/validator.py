"""3-layer validator: schema (Pydantic), data integrity, content sanity.

- Layer 1 (schema): Pydantic catches missing fields / wrong types / unknown enums.
- Layer 2 (data integrity): defer to Phase 1.5 when real data card format is locked.
- Layer 3 (content sanity): narration length, scene type repetition, empty fields.

Errors formatted as human-readable text that can be pasted back to Claude.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from lib.schema import Script

MAX_NARRATION_CHARS_PER_SCENE = 300
MIN_NARRATION_CHARS_PER_SCENE = 5


@dataclass
class ValidationError:
    scene_idx: int
    scene_type: str
    scene_title: str
    message: str
    suggestion: Optional[str] = None


def parse_claude_output(raw: str) -> dict:
    """Strip markdown fences if present, then JSON-parse.

    Claude.ai chats sometimes wrap JSON in ```json fences despite instructions.
    """
    text = raw.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def check_content_sanity(script: Script) -> list[ValidationError]:
    """Layer 3 — narration length + scene type repetition."""
    errors: list[ValidationError] = []
    for idx, scene in enumerate(script.scenes):
        title = _scene_title(scene)
        narration = scene.narration_text.strip()
        if len(narration) < MIN_NARRATION_CHARS_PER_SCENE:
            errors.append(ValidationError(
                idx, scene.type, title,
                f"narration_text quá ngắn ({len(narration)} ký tự, tối thiểu {MIN_NARRATION_CHARS_PER_SCENE}).",
            ))
        if len(narration) > MAX_NARRATION_CHARS_PER_SCENE:
            errors.append(ValidationError(
                idx, scene.type, title,
                f"narration_text quá dài ({len(narration)} ký tự, tối đa {MAX_NARRATION_CHARS_PER_SCENE}).",
                suggestion="Cắt bớt nội dung hoặc tách thành 2 scene.",
            ))

    # Scene type repetition: 3 cùng type liên tiếp
    for i in range(len(script.scenes) - 2):
        t = script.scenes[i].type
        if script.scenes[i + 1].type == t and script.scenes[i + 2].type == t:
            errors.append(ValidationError(
                i + 2, t, _scene_title(script.scenes[i + 2]),
                f"scene type '{t}' lặp 3 lần liên tiếp tại scenes[{i}..{i+2}]. Đa dạng hoá scene type.",
            ))
    return errors


def check_data_integrity(script: Script, data_card_md: str) -> list[ValidationError]:
    """Layer 2 — stub. Real implementation pending data card format spec."""
    return []


def format_errors_for_claude(errors: list[ValidationError]) -> str:
    lines = ["LỖI VALIDATION - sửa các điểm sau rồi trả JSON đầy đủ lại:\n"]
    for e in errors:
        lines.append(f'- scenes[{e.scene_idx}] ({e.scene_type} "{e.scene_title}"):')
        lines.append(f"    {e.message}")
        if e.suggestion:
            lines.append(f"    Gợi ý: {e.suggestion}")
    return "\n".join(lines)


def _scene_title(scene) -> str:
    data = scene.data
    for attr in ("headline", "title", "metric", "cta"):
        if hasattr(data, attr):
            value = getattr(data, attr)
            if value:
                return str(value)
    return scene.id
