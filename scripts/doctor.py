#!/usr/bin/env python3
"""Read-only workstation inventory. Writes one local JSON report; never installs tools."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def probe(command: list[str], timeout: int = 20) -> dict:
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace", check=False)
        return {"command": command, "returncode": p.returncode,
                "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "error": str(exc)}


def inventory() -> dict:
    data = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "kind": "fusion", "os": platform.system(), "os_release": platform.release(),
        "architecture": platform.machine(), "python": sys.version,
        "python_executable": sys.executable, "working_directory": str(Path.cwd()),
        "wsl": bool(os.environ.get("WSL_DISTRO_NAME")) or "microsoft" in platform.release().lower(),
        "container_hint": Path("/.dockerenv").exists(),
        "tools": {}, "cad_runtime_verified": False,
        "note": "Discovery does not establish GUI access, licenses, or real CAD execution.",
    }
    for name in ("git", "code", "codex", "gh", "winget"):
        path = shutil.which(name)
        data["tools"][name] = {"path": path}
        if path:
            data["tools"][name]["version_probe"] = probe([path, "--version"])
    roots = []
    if os.name == "nt" and os.environ.get("APPDATA"):
        base = Path(os.environ["APPDATA"]) / "Autodesk"
        roots = [base / n / "API" for n in ("Autodesk Fusion", "Autodesk Fusion 360")]
    elif platform.system() == "Darwin":
        base = Path.home() / "Library/Application Support/Autodesk"
        roots = [base / n / "API" for n in ("Autodesk Fusion", "Autodesk Fusion 360")]
    data["fusion_api_path_candidates"] = [
        {"path": str(p), "exists": p.is_dir()} for p in roots
    ]
    data["note"] += " Fusion API folders are candidates, not proof of the active configured path."
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path(".local/doctor.json"))
    args = parser.parse_args()
    data = inventory()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Inventory written: {args.out.resolve()}")
    print("This is inventory only; no CAD smoke test was performed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
