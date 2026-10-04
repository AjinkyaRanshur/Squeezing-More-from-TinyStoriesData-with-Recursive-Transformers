# src/rtt/utils/manifest.py
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch


def _git(args: list[str]) -> str:
    """Run a git command and return its output, or 'unknown' if it fails."""
    try:
        result=subprocess.run(["git", *args],capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return "unkonwn"


def write_manifest(run_dir, config: dict, seed: int) -> Path:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True,exist_ok=True)
    status = _git(["status", "--porcelain"])

    if status == "unknown":
        dirty = "unknown"          # git failed, so we can't tell
    else:
        dirty = status != ""       # any output means there are uncommitted changes

    manifest = {

        "git_commit": _git(["rev-parse", "HEAD"]),
        "git_dirty": dirty,
        "sytem_version":sys.version,
        "torch_version":torch.__version__,
        "cuda_version": torch.version.cuda, 
        "numpy_version": np.__version__,
        "device" : torch.cuda.get_device_name(0),
        "config":config,
        "seed":seed,
        "timestamp":datetime.now(timezone.utc).isoformat()

    }

    path = run_dir / "manifest.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    # TODO 8: open path for writing and json.dump(manifest, f, indent=2)
    return path