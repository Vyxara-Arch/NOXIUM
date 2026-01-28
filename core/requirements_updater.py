import json
import os
import re
import subprocess
import sys
from typing import Iterable, Set, Tuple


def _parse_requirements(path: str, seen: Set[str] | None = None) -> Set[str]:
    if seen is None:
        seen = set()
    if not os.path.exists(path):
        return set()

    reqs: Set[str] = set()
    base_dir = os.path.dirname(os.path.abspath(path))
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-r "):
                rel = line[2:].strip()
                sub_path = rel if os.path.isabs(rel) else os.path.join(base_dir, rel)
                if sub_path not in seen:
                    seen.add(sub_path)
                    reqs |= _parse_requirements(sub_path, seen)
                continue
            if line.startswith("-e "):
                continue
            if line.startswith("-"):
                continue
            name = re.split(r"[<=>!~\\[]", line, 1)[0].strip()
            if name:
                reqs.add(name.lower())
    return reqs


def _run_pip(args: list[str], timeout_sec: int) -> Tuple[bool, str]:
    cmd = [sys.executable, "-m", "pip"] + args
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_sec
        )
    except Exception as e:
        return False, str(e)

    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip()
        return False, err or "pip command failed"
    return True, proc.stdout


def check_and_update(
    requirements_path: str = "requirements.txt",
    timeout_sec: int = 180,
    force: bool = False,
) -> Tuple[bool, str]:
    if os.getenv("NOXIUM_SKIP_DEPS_UPDATE") == "1":
        return False, "Skip flag set"

    reqs = _parse_requirements(requirements_path)
    if not reqs:
        return False, "No requirements"

    ok, out = _run_pip(["list", "--outdated", "--format=json"], timeout_sec)
    if not ok:
        return False, f"Update check failed: {out}"

    try:
        outdated = json.loads(out)
    except Exception:
        outdated = []

    outdated_names = {pkg.get("name", "").lower() for pkg in outdated}
    to_update = sorted(outdated_names & reqs)
    if not to_update and not force:
        return False, "Up to date"

    ok, out = _run_pip(
        ["install", "-r", requirements_path, "--upgrade", "--disable-pip-version-check"],
        timeout_sec,
    )
    if not ok:
        return False, f"Update failed: {out}"
    return True, "Updated requirements"
