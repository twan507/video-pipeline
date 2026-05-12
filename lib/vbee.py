"""Vbee TTS client - async polling.

Vbee API is async-only: POST returns request_id, must poll GET /tts/{id} until SUCCESS.
audio_link expires 3 min after SUCCESS - download immediately.

See docs/vbee_api_collection.json for Postman reference.
"""
import os
import time
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://vbee.vn/api/v1"
DEFAULT_CALLBACK = "https://example.com/callback"  # required by API but we poll


class VbeeError(RuntimeError):
    pass


class VbeeClient:
    def __init__(self, token: Optional[str] = None, app_id: Optional[str] = None):
        self.token = token or os.environ["VBEE_TOKEN"]
        self.app_id = app_id or os.environ["VBEE_APPID"]
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {self.token}"

    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: str,
        speed: float = 1.0,
        bitrate: int = 128,
        poll_interval: float = 2.0,
        max_wait_s: float = 60.0,
    ) -> None:
        request_id = self._post_synthesis(text, voice, speed, bitrate)
        audio_link = self._poll_until_success(request_id, poll_interval, max_wait_s)
        self._download(audio_link, output_path)

    def _post_synthesis(self, text: str, voice: str, speed: float, bitrate: int) -> str:
        resp = self.session.post(
            f"{BASE_URL}/tts",
            json={
                "app_id": self.app_id,
                "response_type": "indirect",
                "callback_url": DEFAULT_CALLBACK,
                "input_text": text,
                "voice_code": voice,
                "audio_type": "mp3",
                "bitrate": bitrate,
                "speed_rate": f"{speed:.1f}",
            },
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        if body.get("status") != 1:
            raise VbeeError(body.get("error_message") or f"POST failed: {body}")
        return body["result"]["request_id"]

    def _poll_until_success(self, request_id: str, interval: float, max_wait_s: float) -> str:
        deadline = time.time() + max_wait_s
        while time.time() < deadline:
            time.sleep(interval)
            resp = self.session.get(f"{BASE_URL}/tts/{request_id}", timeout=30)
            resp.raise_for_status()
            body = resp.json()
            status = body["result"]["status"]
            if status == "SUCCESS":
                return body["result"]["audio_link"]
            if status == "FAILURE":
                raise VbeeError(f"Synthesis failed: {body}")
        raise VbeeError(f"Polling timeout after {max_wait_s}s for request {request_id}")

    def _download(self, url: str, path: Path) -> None:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(resp.content)
