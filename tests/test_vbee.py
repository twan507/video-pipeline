from pathlib import Path

import pytest
import requests_mock

from lib.vbee import VbeeClient, VbeeError


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("VBEE_TOKEN", "fake-jwt")
    monkeypatch.setenv("VBEE_APPID", "fake-app-id")
    return VbeeClient()


def test_synthesize_writes_file_on_success(client, tmp_path):
    out = tmp_path / "out.mp3"
    with requests_mock.Mocker() as m:
        m.post(
            "https://vbee.vn/api/v1/tts",
            json={"status": 1, "result": {"request_id": "req-123", "status": "IN_PROGRESS"}},
        )
        m.get(
            "https://vbee.vn/api/v1/tts/req-123",
            json={"status": 1, "result": {"status": "SUCCESS", "audio_link": "https://example.com/a.mp3"}},
        )
        m.get("https://example.com/a.mp3", content=b"FAKE_MP3_BYTES")

        client.synthesize("hello", out, voice="v1", speed=1.0, poll_interval=0)

    assert out.read_bytes() == b"FAKE_MP3_BYTES"


def test_synthesize_sends_correct_payload(client, tmp_path):
    with requests_mock.Mocker() as m:
        m.post(
            "https://vbee.vn/api/v1/tts",
            json={"status": 1, "result": {"request_id": "r1"}},
        )
        m.get(
            "https://vbee.vn/api/v1/tts/r1",
            json={"status": 1, "result": {"status": "SUCCESS", "audio_link": "https://x/a.mp3"}},
        )
        m.get("https://x/a.mp3", content=b"x")
        client.synthesize("Xin chao", tmp_path / "o.mp3", voice="v1", speed=0.9, poll_interval=0)

        sent = m.request_history[0].json()
        assert sent["app_id"] == "fake-app-id"
        assert sent["input_text"] == "Xin chao"
        assert sent["voice_code"] == "v1"
        assert sent["speed_rate"] == "0.9"
        assert sent["response_type"] == "indirect"
        assert sent["callback_url"] == "https://example.com/callback"


def test_synthesize_raises_on_post_failure(client, tmp_path):
    with requests_mock.Mocker() as m:
        m.post(
            "https://vbee.vn/api/v1/tts",
            json={"status": 0, "error_message": "bad token"},
        )
        with pytest.raises(VbeeError, match="bad token"):
            client.synthesize("hi", tmp_path / "o.mp3", voice="v1", speed=1.0)


def test_synthesize_raises_on_synthesis_failure(client, tmp_path):
    with requests_mock.Mocker() as m:
        m.post(
            "https://vbee.vn/api/v1/tts",
            json={"status": 1, "result": {"request_id": "r1"}},
        )
        m.get(
            "https://vbee.vn/api/v1/tts/r1",
            json={"status": 1, "result": {"status": "FAILURE"}},
        )
        with pytest.raises(VbeeError, match="Synthesis failed"):
            client.synthesize("hi", tmp_path / "o.mp3", voice="v1", speed=1.0, poll_interval=0)


def test_synthesize_raises_on_polling_timeout(client, tmp_path):
    with requests_mock.Mocker() as m:
        m.post(
            "https://vbee.vn/api/v1/tts",
            json={"status": 1, "result": {"request_id": "r1"}},
        )
        m.get(
            "https://vbee.vn/api/v1/tts/r1",
            json={"status": 1, "result": {"status": "IN_PROGRESS"}},
        )
        with pytest.raises(VbeeError, match="timeout"):
            client.synthesize("hi", tmp_path / "o.mp3", voice="v1", speed=1.0,
                              poll_interval=0, max_wait_s=0.05)


@pytest.mark.live
def test_synthesize_live(tmp_path):
    """Real API call. Costs ~1 credit. Run via: pytest -m live"""
    client = VbeeClient()  # reads VBEE_TOKEN, VBEE_APPID from .env
    out = tmp_path / "live.mp3"
    client.synthesize(
        "Xin chao, day la test tich hop.",
        out,
        voice="hn_male_phuthang_news65dt_44k-fhg",
        speed=1.0,
    )
    assert out.stat().st_size > 1000
