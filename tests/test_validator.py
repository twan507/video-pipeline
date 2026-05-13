import pytest

from lib.schema import Script
from lib.validator import (
    ValidationError,
    check_content_sanity,
    format_errors_for_claude,
    parse_claude_output,
)

BASE_SCRIPT = {
    "video_id": "v1",
    "template": "bulletin",
    "meta": {"title": "T", "created_at": "2026-05-12T00:00:00+07:00"},
    "scenes": [
        {"id": "s01", "type": "intro", "narration_text": "Bản tin tuần",
         "data": {"headline": "H", "category": "C"}},
        {"id": "s02", "type": "metric", "narration_text": "Lợi nhuận giảm",
         "data": {"metric": "M", "current_value": 1.0, "previous_value": 2.0}},
        {"id": "s03", "type": "outro", "narration_text": "Cảm ơn các bạn",
         "data": {"cta": "Theo dõi"}},
    ],
}


def test_parse_claude_output_plain_json():
    raw = '{"a": 1}'
    assert parse_claude_output(raw) == {"a": 1}


def test_parse_claude_output_strips_json_fence():
    raw = '```json\n{"a": 1}\n```'
    assert parse_claude_output(raw) == {"a": 1}


def test_parse_claude_output_strips_bare_fence():
    raw = '```\n{"a": 1}\n```'
    assert parse_claude_output(raw) == {"a": 1}


def test_content_sanity_passes_clean_script():
    script = Script.model_validate(BASE_SCRIPT)
    assert check_content_sanity(script) == []


def test_content_sanity_flags_short_narration():
    bad = {**BASE_SCRIPT, "scenes": [
        {**BASE_SCRIPT["scenes"][0], "narration_text": "x"},
        *BASE_SCRIPT["scenes"][1:],
    ]}
    script = Script.model_validate(bad)
    errors = check_content_sanity(script)
    assert len(errors) == 1
    assert "quá ngắn" in errors[0].message
    assert errors[0].scene_idx == 0


def test_content_sanity_flags_long_narration():
    long_text = "x" * 700
    bad = {**BASE_SCRIPT, "scenes": [
        {**BASE_SCRIPT["scenes"][0], "narration_text": long_text},
        *BASE_SCRIPT["scenes"][1:],
    ]}
    script = Script.model_validate(bad)
    errors = check_content_sanity(script)
    assert any("quá dài" in e.message for e in errors)


def test_content_sanity_flags_3_same_type_in_a_row():
    bad = {**BASE_SCRIPT, "scenes": [
        {"id": f"s0{i}", "type": "metric", "narration_text": "Lợi nhuận giảm",
         "data": {"metric": "M", "current_value": 1.0, "previous_value": 2.0}}
        for i in range(1, 4)
    ]}
    script = Script.model_validate(bad)
    errors = check_content_sanity(script)
    assert any("lặp 3 lần" in e.message for e in errors)


def test_format_errors_for_claude_renders_all_fields():
    errors = [
        ValidationError(2, "kpi", "Lợi nhuận", "thiếu trường delta", "delta = current - previous"),
        ValidationError(0, "headline", "Big news", "narration quá ngắn"),
    ]
    out = format_errors_for_claude(errors)
    assert "LỖI VALIDATION" in out
    assert 'scenes[2] (kpi "Lợi nhuận")' in out
    assert "thiếu trường delta" in out
    assert "Gợi ý:" in out
    assert "narration quá ngắn" in out
