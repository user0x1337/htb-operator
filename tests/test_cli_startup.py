import os
import subprocess
import sys
from pathlib import Path


def test_init_help_starts_with_unavailable_libarchive(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "htb_operator", "init", "--help"],
        cwd=Path(__file__).resolve().parents[1],
        env={
            **os.environ,
            "LIBARCHIVE": str(tmp_path / "missing-libarchive"),
            "HTB_TERMINAL_STORE_DIR": str(tmp_path),
        },
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert "usage: htb-operator init" in result.stdout
