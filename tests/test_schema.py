import pytest
from pydantic import ValidationError

from lib.schema import DEFAULT_VOICE, Meta, Script


VALID_SCRIPT = {
    "video_id": "2026-05-12_test",
    "template": "bulletin",
    "meta": {"title": "Test", "created_at": "2026-05-12T00:00:00+07:00"},
    "scenes": [
        {
            "id": "s01",
            "type": "intro",
            "narration_text": "Hello",
            "data": {"headline": "Big news", "category": "Markets"},
        },
        {
            "id": "s02",
            "type": "ranking",
            "narration_text": "Top movers",
            "data": {
                "title": "Top tăng giá",
                "items": [
                    {"rank": 1, "label": "VNM", "value": 100.5, "change_pct": 5.2},
                    {"rank": 2, "label": "FPT", "value": 95.0, "change_pct": 3.8},
                ],
            },
        },
        {
            "id": "s03",
            "type": "metric",
            "narration_text": "Profit margin",
            "data": {"metric": "Tỷ suất lợi nhuận", "current_value": 18.0, "previous_value": 22.4, "unit": "%"},
        },
        {
            "id": "s04",
            "type": "outro",
            "narration_text": "Follow us",
            "data": {"cta": "Theo dõi VBSE để cập nhật mới nhất", "handle": "@vbse"},
        },
    ],
}


def test_parses_valid_bulletin_script():
    script = Script.model_validate(VALID_SCRIPT)
    assert script.video_id == "2026-05-12_test"
    assert len(script.scenes) == 4
    assert script.scenes[0].type == "intro"
    assert script.scenes[1].data.items[0].label == "VNM"


def test_meta_defaults_to_locked_voice_and_format():
    m = Meta(title="x", created_at="2026-05-12T00:00:00+07:00")
    assert m.voice == DEFAULT_VOICE
    assert m.fps == 30
    assert m.width == 1080
    assert m.height == 1080
    assert m.speed == 1.0


def test_rejects_unknown_scene_type():
    bad = {**VALID_SCRIPT, "scenes": [{"id": "s01", "type": "bogus", "narration_text": "x", "data": {}}]}
    with pytest.raises(ValidationError):
        Script.model_validate(bad)


def test_rejects_missing_required_field():
    bad = {**VALID_SCRIPT, "scenes": [{"id": "s01", "type": "intro", "narration_text": "x",
                                        "data": {"category": "Markets"}}]}  # missing headline
    with pytest.raises(ValidationError):
        Script.model_validate(bad)


def test_rejects_invalid_template():
    bad = {**VALID_SCRIPT, "template": "foobar"}
    with pytest.raises(ValidationError):
        Script.model_validate(bad)


def test_roundtrip_json():
    script = Script.model_validate(VALID_SCRIPT)
    raw = script.model_dump_json()
    again = Script.model_validate_json(raw)
    assert again.video_id == script.video_id
    assert again.scenes[2].data.current_value == 18.0


def test_ranking_item_value_optional():
    """Sector rank không cần value, chỉ change_pct"""
    s = {**VALID_SCRIPT, "scenes": [
        {"id": "s01", "type": "ranking", "narration_text": "x" * 10, "data": {
            "title": "Top sectors",
            "items": [
                {"rank": 1, "label": "Bảo hiểm", "change_pct": 2.63},
            ],
        }},
    ]}
    script = Script.model_validate(s)
    assert script.scenes[0].data.items[0].value is None
