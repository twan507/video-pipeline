# Vbee TTS Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build async polling TTS client + audio cache + postprocess that powers notebook Cell 5 (audio enrichment). Resolves spec section 8 + Phase 0 POC blocker.

**Architecture:** Vbee API is **async-only** — `POST /tts` returns `request_id` with `status=IN_PROGRESS`, must poll `GET /tts/{request_id}` until `status=SUCCESS` then download `audio_link` within 3 minutes. Cache keyed by `sha256(narration_text|voice|speed)` skips API call when narration unchanged. pydub trims trailing silence and normalizes peak post-synthesis. Postman doc reference: `docs/vbee_api_collection.json`.

**Tech Stack:** Python 3.11, requests, python-dotenv, pydub, mutagen, pytest, requests-mock.

**Locked decisions** (confirmed before drafting):
- **Voice:** `hn_male_phuthang_news65dt_44k-fhg` (HN - Anh Khôi, news, 44k). 1 giọng cho mọi template per spec section 19.
- **Strategy:** polling, không webhook. `callback_url` field truyền `https://example.com/callback` (Vbee yêu cầu nhưng không bị gọi khi ta poll).
- **Polling:** 2s interval, 60s timeout.
- **Env keys:** `VBEE_TOKEN` (JWT), `VBEE_APPID` (UUID).
- **Audio format:** mp3, bitrate 128.

**Out of scope (separate plan later):** `lib/schema.py` (Pydantic models), `lib/validator.py`, `lib/data_card.py`, `lib/render.py`, notebook blueprint cells, Remotion components.

**Prerequisites:**
- `.env` file with real `VBEE_TOKEN` + `VBEE_APPID` (user creates from `.env.example`)
- Python 3.11+ venv activated
- `git init` đã chạy (optional — plan không có commit steps, user tự commit khi muốn)

---

## File structure

| File | Purpose |
|---|---|
| `.env.example` | Document required secrets |
| `pyproject.toml` | Pin runtime + test deps |
| `scripts/poc_vbee.py` | Phase 0 standalone POC — run once |
| `lib/vbee.py` | `VbeeClient` async polling |
| `lib/cache.py` | Pure functions `audio_cache_key`, `audio_path` |
| `lib/audio.py` | pydub wrappers `trim_silence`, `normalize_peak`, `get_duration` |
| `tests/__init__.py` | Empty package marker |
| `tests/conftest.py` | pytest config (live marker) |
| `tests/fixtures/sample.mp3` | Real MP3 cho audio tests (copy từ POC output) |
| `tests/test_cache.py` | Unit tests cho cache |
| `tests/test_audio.py` | Unit tests cho audio (sample.mp3 fixture) |
| `tests/test_vbee.py` | Mock unit tests + 1 live integration test |

---

### Task 1: Phase 0 POC — verify Vbee end-to-end

POC standalone script chứng minh: auth đúng, voice_code hợp lệ, polling work, audio_link download được. Output là file MP3 nghe được. Đây là blocker phải pass trước khi viết lib/.

**Files:**
- Modify: `.env.example`
- Modify: `pyproject.toml`
- Create: `scripts/poc_vbee.py`

- [ ] **Step 1: Update `.env.example`**

Replace toàn bộ nội dung:

```
# Copy to .env and fill in. Never commit .env.
VBEE_TOKEN=
VBEE_APPID=
```

- [ ] **Step 2: User creates real `.env`**

```bash
cp .env.example .env
# Mở .env, paste VBEE_TOKEN (JWT) và VBEE_APPID (UUID) từ Vbee dashboard
```

- [ ] **Step 3: Install runtime deps**

```bash
pip install requests python-dotenv
```

- [ ] **Step 4: Write `scripts/poc_vbee.py`**

```python
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
```

- [ ] **Step 5: Run POC**

```bash
python scripts/poc_vbee.py
```

Expected output (rough timing):
```
POST /tts with 68 chars, voice=hn_male_phuthang_news65dt_44k-fhg
POST response: {'result': {'request_id': '...', 'status': 'IN_PROGRESS', ...}, 'status': 1}
request_id=..., polling every 2s up to 60s...
  attempt 1: status=IN_PROGRESS, progress=...
  attempt 2: status=SUCCESS, progress=...
Downloading https://...amazonaws.com/...
DONE in ~5-15s: scripts/poc_output.mp3 (~50000 bytes)
```

Verify: open `scripts/poc_output.mp3`, listen — phải là giọng nam Hà Nội, kiểu bản tin, đọc đúng câu test.

- [ ] **Step 6: Record findings in `memory.md` activity log**

Note (in `memory.md` under 2026-05-11):
- Time elapsed cho ~68 chars
- Voice quality (đúng "Anh Khôi" giọng news? quality OK?)
- Polling cần bao nhiêu attempts
- Bất kỳ error/warning nào

If POC fails, **STOP** và debug trước khi qua Task 2. Common failures:
- 401 Unauthorized → token sai hoặc hết hạn
- 400 Bad Request → app_id sai hoặc voice_code không tồn tại
- Polling timeout → check Vbee dashboard xem request có submit không

---

### Task 2: `lib/cache.py` — pure-function audio cache

Trivial pure functions, full TDD.

**Files:**
- Modify: `pyproject.toml` (add pytest)
- Create: `tests/__init__.py` (empty)
- Create: `tests/conftest.py`
- Create: `tests/test_cache.py`
- Modify: `lib/cache.py`

- [ ] **Step 1: Install test deps**

```bash
pip install pytest requests-mock
```

- [ ] **Step 2: Update `pyproject.toml`** — add test deps and pytest config:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "requests-mock",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "live: hits real Vbee API (costs credits, skip by default)",
]
addopts = "-m 'not live'"
```

- [ ] **Step 3: Create `tests/__init__.py`** (empty file)

- [ ] **Step 4: Create `tests/conftest.py`**

```python
"""Shared pytest fixtures."""
import sys
from pathlib import Path

# Make lib/ importable
sys.path.insert(0, str(Path(__file__).parent.parent))
```

- [ ] **Step 5: Write `tests/test_cache.py`**

```python
from types import SimpleNamespace
from lib.cache import audio_cache_key, audio_path


def make_scene(id="s01", text="Xin chao"):
    return SimpleNamespace(id=id, narration_text=text)


def test_cache_key_starts_with_scene_id():
    key = audio_cache_key(make_scene("s01"), voice="v1", speed=1.0)
    assert key.startswith("s01_")
    assert key.endswith(".mp3")


def test_cache_key_changes_with_text():
    k1 = audio_cache_key(make_scene(text="A"), "v1", 1.0)
    k2 = audio_cache_key(make_scene(text="B"), "v1", 1.0)
    assert k1 != k2


def test_cache_key_changes_with_voice():
    k1 = audio_cache_key(make_scene(), "v1", 1.0)
    k2 = audio_cache_key(make_scene(), "v2", 1.0)
    assert k1 != k2


def test_cache_key_changes_with_speed():
    k1 = audio_cache_key(make_scene(), "v1", 1.0)
    k2 = audio_cache_key(make_scene(), "v1", 0.9)
    assert k1 != k2


def test_cache_key_stable():
    s = make_scene()
    assert audio_cache_key(s, "v1", 1.0) == audio_cache_key(s, "v1", 1.0)


def test_audio_path_uses_dir(tmp_path):
    p = audio_path(make_scene(), tmp_path, voice="v1", speed=1.0)
    assert p.parent == tmp_path
    assert p.suffix == ".mp3"
```

- [ ] **Step 6: Run tests, verify FAIL** (function not defined)

```bash
pytest tests/test_cache.py -v
```

- [ ] **Step 7: Implement `lib/cache.py`**

```python
"""Audio cache keyed by hash(narration_text, voice, speed)."""
import hashlib
from pathlib import Path
from typing import Any

DEFAULT_VOICE = "hn_male_phuthang_news65dt_44k-fhg"


def audio_cache_key(scene: Any, voice: str, speed: float) -> str:
    payload = f"{scene.narration_text}|{voice}|{speed}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"{scene.id}_{digest}.mp3"


def audio_path(scene: Any, audio_dir: Path, voice: str = DEFAULT_VOICE, speed: float = 1.0) -> Path:
    return audio_dir / audio_cache_key(scene, voice, speed)
```

- [ ] **Step 8: Run tests, verify PASS**

```bash
pytest tests/test_cache.py -v
```

---

### Task 3: `lib/audio.py` — pydub postprocess wrappers

Cần 1 sample MP3 thật cho test (copy từ Task 1 POC output).

**Files:**
- Modify: `pyproject.toml` (add pydub, mutagen)
- Create: `tests/fixtures/sample.mp3` (copy)
- Create: `tests/test_audio.py`
- Modify: `lib/audio.py`

**Pre-requisite:** ffmpeg installed (pydub requires it for MP3). On Windows: `winget install ffmpeg` or download from ffmpeg.org and add to PATH.

- [ ] **Step 1: Verify ffmpeg available**

```bash
ffmpeg -version
```

Expected: prints version. If not found, install before continuing.

- [ ] **Step 2: Install audio deps**

```bash
pip install pydub mutagen
```

- [ ] **Step 3: Copy POC output as test fixture**

```bash
mkdir -p tests/fixtures
cp scripts/poc_output.mp3 tests/fixtures/sample.mp3
```

- [ ] **Step 4: Update `pyproject.toml`** — add to `dependencies`:

```toml
dependencies = [
    "pydantic>=2",
    "requests",
    "python-dotenv",
    "pyperclip",
    "pydub",
    "mutagen",
    "pydantic2ts",
    "jupyterlab",
    "ipython",
]
```

- [ ] **Step 5: Write `tests/test_audio.py`**

```python
import shutil
from pathlib import Path

import pytest

from lib.audio import get_duration, normalize_peak, trim_silence

FIXTURE = Path(__file__).parent / "fixtures" / "sample.mp3"


@pytest.fixture
def tmp_mp3(tmp_path):
    dst = tmp_path / "audio.mp3"
    shutil.copy(FIXTURE, dst)
    return dst


def test_get_duration_returns_positive_float(tmp_mp3):
    d = get_duration(tmp_mp3)
    assert isinstance(d, float)
    assert d > 0


def test_trim_silence_keeps_valid_mp3(tmp_mp3):
    trim_silence(tmp_mp3)
    assert get_duration(tmp_mp3) > 0


def test_normalize_peak_preserves_duration(tmp_mp3):
    d_before = get_duration(tmp_mp3)
    normalize_peak(tmp_mp3)
    d_after = get_duration(tmp_mp3)
    assert abs(d_after - d_before) < 0.2  # mp3 re-encode can shift by ~50ms
```

- [ ] **Step 6: Run tests, verify FAIL**

```bash
pytest tests/test_audio.py -v
```

- [ ] **Step 7: Implement `lib/audio.py`**

```python
"""Audio postprocess: trim trailing silence, normalize peak, read duration."""
from pathlib import Path

from mutagen.mp3 import MP3
from pydub import AudioSegment, silence


def trim_silence(path: Path, threshold_db: int = -40, padding_ms: int = 100) -> None:
    """Strip leading/trailing silence chunks. Vbee adds ~200ms silence padding."""
    audio = AudioSegment.from_mp3(str(path))
    chunks = silence.split_on_silence(
        audio,
        min_silence_len=300,
        silence_thresh=threshold_db,
        keep_silence=padding_ms,
    )
    if not chunks:
        return
    result = chunks[0]
    for chunk in chunks[1:]:
        result += chunk
    result.export(str(path), format="mp3", bitrate="128k")


def normalize_peak(path: Path, target_dbfs: float = -1.0) -> None:
    """Apply gain so max peak hits target_dbfs (default -1 dBFS)."""
    audio = AudioSegment.from_mp3(str(path))
    change = target_dbfs - audio.max_dBFS
    audio.apply_gain(change).export(str(path), format="mp3", bitrate="128k")


def get_duration(path: Path) -> float:
    return round(MP3(str(path)).info.length, 3)
```

- [ ] **Step 8: Run tests, verify PASS**

---

### Task 4: `lib/vbee.py` — VbeeClient class

Refactor Task 1 POC into reusable class. Mock-based unit tests + 1 live integration test.

**Files:**
- Create: `tests/test_vbee.py`
- Modify: `lib/vbee.py`

- [ ] **Step 1: Write `tests/test_vbee.py`**

```python
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
```

- [ ] **Step 2: Run tests, verify FAIL**

```bash
pytest tests/test_vbee.py -v
```

- [ ] **Step 3: Implement `lib/vbee.py`**

```python
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
```

- [ ] **Step 4: Run unit tests, verify PASS**

```bash
pytest tests/test_vbee.py -v
```

5 unit tests pass (live test skipped).

- [ ] **Step 5: Run live integration test**

```bash
pytest tests/test_vbee.py -v -m live
```

Expected: 1 test passes in ~5-15s. Costs ~1 credit. If FAIL, check Task 1 POC output for divergence.

- [ ] **Step 6: Verify full suite green**

```bash
pytest -v
```

Cache + audio + vbee unit tests pass (live skipped by default per pyproject.toml `addopts`).

---

### Task 5: Wire `memory.md` with Phase 0 outcomes

- [ ] **Step 1: Update `memory.md` — mark Phase 0 done, lock voice decision**

Modify section `## Phase tracker`:
- Change "0" status from `TODO` to `DONE 2026-05-11` with note "POC verified, voice + polling work"

Modify section `## Locked decisions`:
- Update item 2 ("Voice config"): replace tentative `anh_khoi` with concrete `hn_male_phuthang_news65dt_44k-fhg`

Modify section `## Blockers`: remove the Phase 0 checklist (replace with "All Phase 0 items resolved on 2026-05-11").

Append to `## Activity log` under `### 2026-05-11`:
```
- Vbee Phase 0 POC: token + app_id validated. Voice `hn_male_phuthang_news65dt_44k-fhg`
  synthesizes in ~Xs for 68 chars. Audio quality OK / not OK.
- Locked: polling strategy (no webhook), callback_url placeholder, env keys VBEE_TOKEN + VBEE_APPID.
- Implemented lib/vbee.py (async polling), lib/cache.py, lib/audio.py with pytest coverage.
```

(Replace placeholder X with real numbers from POC run.)

- [ ] **Step 2: Update `pyproject.toml`** to ensure deps list is final

After all tasks: dependencies should include `requests`, `python-dotenv`, `pydub`, `mutagen`, `pydantic>=2` (kept for next plan), and dev extras `pytest`, `requests-mock`.

---

## Verification checklist

After all tasks done, run:
```bash
pytest -v                    # all unit tests green, live skipped
pytest -v -m live            # live test green, costs 1 credit
python scripts/poc_vbee.py   # POC still works (sanity)
ls tests/fixtures/sample.mp3 # fixture present
```

Then proceed to next plan (lib/schema.py + lib/validator.py + lib/data_card.py).
