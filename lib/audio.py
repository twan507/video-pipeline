"""Audio postprocess: trim trailing silence, normalize peak, read duration.

Uses portable ffmpeg shipped with `imageio-ffmpeg` so no system install needed.
"""
from pathlib import Path

import imageio_ffmpeg
from mutagen.mp3 import MP3
from pydub import AudioSegment, silence

AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()


def trim_silence(path: Path, threshold_db: int = -40, padding_ms: int = 100) -> None:
    """Strip leading/trailing silence chunks. Vbee adds ~200ms silence padding."""
    audio = AudioSegment.from_file(str(path), format="mp3", codec="mp3")
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
    audio = AudioSegment.from_file(str(path), format="mp3", codec="mp3")
    change = target_dbfs - audio.max_dBFS
    audio.apply_gain(change).export(str(path), format="mp3", bitrate="128k")


def get_duration(path: Path) -> float:
    return round(MP3(str(path)).info.length, 3)
