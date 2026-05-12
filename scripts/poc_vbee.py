"""POC Vbee TTS — POST -> poll -> download. Phase 0 verification.

Usage: python scripts/poc_vbee.py
"""
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["VBEE_TOKEN"]
APP_ID = os.environ["VBEE_APPID"]
VOICE = "hn_male_phuthang_news65dt_44k-fhg"  # HN - Anh Khoi, news style, 44k
SAMPLE_TEXT = "Xin chao, day la bai kiem tra tong hop giong noi cho du an VBSE."
OUTPUT_PATH = Path("scripts/poc_output.mp3")

BASE_URL = "https://vbee.vn/api/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def main() -> int:
    print(f"POST /tts with {len(SAMPLE_TEXT)} chars, voice={VOICE}")
    t0 = time.time()

    resp = requests.post(
        f"{BASE_URL}/tts",
        headers=HEADERS,
        json={
            "app_id": APP_ID,
            "response_type": "indirect",
            "callback_url": "https://example.com/callback",
            "input_text": SAMPLE_TEXT,
            "voice_code": VOICE,
            "audio_type": "mp3",
            "bitrate": 128,
            "speed_rate": "1.0",
        },
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    print(f"POST response: {body}")
    if body.get("status") != 1:
        print(f"POST failed: {body}")
        return 1

    request_id = body["result"]["request_id"]
    print(f"request_id={request_id}, polling every 2s up to 60s...")

    audio_link = None
    for attempt in range(30):
        time.sleep(2)
        poll = requests.get(f"{BASE_URL}/tts/{request_id}", headers=HEADERS, timeout=30)
        poll.raise_for_status()
        poll_body = poll.json()
        status = poll_body["result"]["status"]
        progress = poll_body["result"].get("progress", "?")
        print(f"  attempt {attempt+1}: status={status}, progress={progress}")
        if status == "SUCCESS":
            audio_link = poll_body["result"]["audio_link"]
            break
        if status == "FAILURE":
            print(f"Synthesis failed: {poll_body}")
            return 1

    if not audio_link:
        print("Timed out waiting for SUCCESS")
        return 1

    print(f"Downloading {audio_link}")
    audio_resp = requests.get(audio_link, timeout=60)
    audio_resp.raise_for_status()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(audio_resp.content)

    elapsed = time.time() - t0
    print(f"DONE in {elapsed:.1f}s: {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
