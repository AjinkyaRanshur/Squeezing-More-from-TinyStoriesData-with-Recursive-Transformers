"""Save everything to GitHub in one command.

Usage (from the repo root, with the venv active):
    python scripts/sync.py "what changed"
    python scripts/sync.py                 # falls back to a timestamped message

What it does, in order:
  1. Regenerates requirements-lock.txt (UTF-8, without the editable rtt package).
  2. Stages every change that .gitignore allows.
  3. Refuses to continue if a staged file is bigger than MAX_MB
     (protects against accidentally pushing a checkpoint or dataset).
  4. Commits, pulls any remote changes (rebase), and pushes.
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_MB = 50


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"\n git {' '.join(args)} failed:\n{result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()


def refresh_lock_file() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--exclude-editable"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("! could not run pip freeze; lock file left unchanged")
        return
    (ROOT / "requirements-lock.txt").write_text(result.stdout, encoding="utf-8", newline="\n")


def main() -> None:
    message = " ".join(sys.argv[1:]).strip() or f"update {datetime.now():%Y-%m-%d %H:%M}"

    refresh_lock_file()
    git("add", "-A")

    staged = [f for f in git("diff", "--cached", "--name-only").splitlines() if f]
    too_big = [
        f for f in staged
        if (ROOT / f).is_file() and (ROOT / f).stat().st_size > MAX_MB * 1024 * 1024
    ]
    if too_big:
        git("reset", "-q")
        print(f"Stopped: these files are over {MAX_MB} MB. Add them to .gitignore first:")
        for f in too_big:
            print("   ", f)
        sys.exit(1)

    if staged:
        print(f"Committing {len(staged)} file(s):")
        for f in staged:
            print("   ", f)
        git("commit", "-q", "-m", message)
    else:
        print("Nothing new to commit.")

    git("pull", "-q", "--rebase")
    git("push", "-q")
    print(f"Pushed. HEAD is now {git('rev-parse', '--short', 'HEAD')}: {git('log', '-1', '--format=%s')}")


if __name__ == "__main__":
    main()