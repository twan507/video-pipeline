import json
from unittest.mock import patch

import pytest

from lib.render import RemotionRenderError, render_video


def _completed(returncode=0, stdout="", stderr=""):
    class R:
        pass
    r = R()
    r.returncode = returncode
    r.stdout = stdout
    r.stderr = stderr
    return r


def test_render_video_builds_correct_command(tmp_path):
    with patch("lib.render.subprocess.run", return_value=_completed()) as mock_run, \
         patch("lib.render._find_npx", return_value="npx"):
        out = render_video(template="bulletin", video_id="2026-05-12_test", project_root=tmp_path)

        cmd = mock_run.call_args[0][0]
        assert cmd[0:3] == ["npx", "remotion", "render"]
        assert cmd[3] == "src/Root.tsx"
        assert cmd[4] == "bulletin"
        assert str(out) in cmd
        props_idx = cmd.index("--props") + 1
        assert json.loads(cmd[props_idx]) == {"scriptPath": "runs/2026-05-12_test/script.json"}
        assert "--concurrency=4" in cmd
        assert "--crf=18" in cmd

        assert mock_run.call_args.kwargs["cwd"] == tmp_path / "remotion"


def test_render_video_creates_output_dir(tmp_path):
    with patch("lib.render.subprocess.run", return_value=_completed()), \
         patch("lib.render._find_npx", return_value="npx"):
        out = render_video("bulletin", "v1", tmp_path)
    assert out.parent.exists()
    assert out == tmp_path / "outputs" / "v1" / "render.mp4"


def test_render_video_raises_on_failure(tmp_path):
    with patch("lib.render.subprocess.run",
               return_value=_completed(returncode=1, stdout="oops", stderr="boom")), \
         patch("lib.render._find_npx", return_value="npx"):
        with pytest.raises(RemotionRenderError, match="boom"):
            render_video("bulletin", "v1", tmp_path)


def test_render_video_appends_extra_args(tmp_path):
    with patch("lib.render.subprocess.run", return_value=_completed()) as mock_run, \
         patch("lib.render._find_npx", return_value="npx"):
        render_video("bulletin", "v1", tmp_path, extra_args=["--quiet", "--gl=swiftshader"])
        cmd = mock_run.call_args[0][0]
        assert "--quiet" in cmd
        assert "--gl=swiftshader" in cmd


def test_find_npx_raises_when_missing():
    from lib.render import _find_npx
    with patch("lib.render.shutil.which", return_value=None):
        with pytest.raises(RemotionRenderError, match="npx not found"):
            _find_npx()
