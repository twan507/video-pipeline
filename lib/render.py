"""Subprocess wrapper to invoke Remotion CLI from notebook.

Requires Node.js + `npm install` in remotion/ folder. See spec section 10.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class RemotionRenderError(RuntimeError):
    pass


def _find_npx() -> str:
    """Resolve npx executable. On Windows it's `npx.cmd`; Python subprocess
    doesn't auto-append `.cmd` so we must find it explicitly.
    """
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if npx is None:
        raise RemotionRenderError(
            "npx not found on PATH. Install Node.js and restart Jupyter / terminal."
        )
    return npx


def render_video(
    template: str,
    video_id: str,
    project_root: Path,
    crf: int = 18,
    concurrency: int = 4,
    extra_args: Optional[list[str]] = None,
) -> Path:
    """Render via `npx remotion render`. Returns absolute path to MP4 output."""
    remotion_dir = project_root / "remotion"
    script_rel = f"runs/{video_id}/script.json"
    output_path = project_root / "outputs" / video_id / "render.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        _find_npx(), "remotion", "render",
        "src/Root.tsx",
        template,
        str(output_path),
        "--props", json.dumps({"scriptPath": script_rel}),
        f"--concurrency={concurrency}",
        f"--crf={crf}",
        "--log=info",
    ]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, cwd=remotion_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RemotionRenderError(
            f"Remotion render failed (code {result.returncode}):\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )
    return output_path
