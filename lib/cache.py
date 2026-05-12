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
