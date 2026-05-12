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
