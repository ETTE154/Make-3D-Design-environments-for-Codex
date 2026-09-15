#!/usr/bin/env python3
"""Verify actual Fusion smoke export files and independently measure STL coordinates."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stl_dimensions(path: Path) -> tuple[list[float], int]:
    data = path.read_bytes()
    if len(data) > 100_000_000:
        raise ValueError("Smoke STL unexpectedly exceeds 100 MB")
    points = []
    triangles = 0
    if len(data) >= 84 and 84 + 50 * struct.unpack_from("<I", data, 80)[0] == len(data):
        triangles = struct.unpack_from("<I", data, 80)[0]
        for index in range(triangles):
            values = struct.unpack_from("<12fH", data, 84 + 50 * index)
            points.extend([values[3:6], values[6:9], values[9:12]])
    else:
        try:
            text = data.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ValueError("Neither a supported binary nor ASCII STL") from exc
        if not text.lstrip().lower().startswith("solid"):
            raise ValueError("Invalid ASCII STL header")
        for line in text.splitlines():
            words = line.strip().split()
            if words and words[0].lower() == "vertex":
                if len(words) != 4:
                    raise ValueError("Invalid vertex record")
                points.append(tuple(float(v) for v in words[1:]))
        if len(points) % 3:
            raise ValueError("STL vertices do not form complete triangles")
        triangles = len(points) // 3
    if triangles == 0 or not points:
        raise ValueError("STL has no triangles")
    if not all(math.isfinite(v) for point in points for v in point):
        raise ValueError("Non-finite STL coordinate")
    dimensions = [max(p[axis] for p in points) - min(p[axis] for p in points) for axis in range(3)]
    return dimensions, triangles


def verify(run_dir: Path) -> dict:
    run_dir = run_dir.resolve()
    result = {"status": "FAILED", "run_dir": str(run_dir), "print_ready": False,
              "note": "Consistency/mesh checks do not certify CAD execution or physical print safety."}
    try:
        report = json.loads((run_dir / "fusion-report.json").read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise ValueError("Fusion report must be a JSON object")
        if not isinstance(report.get("outputs"), dict):
            raise ValueError("Fusion output metadata must be a JSON object")
        if report.get("status") != "CAD_SMOKE_PASSED":
            raise ValueError("Fusion report does not record a successful CAD smoke test")
        if report.get("run_id") != run_dir.name:
            raise ValueError("Report run ID and evidence directory do not match")
        if not report.get("fusion_version") or not report.get("document_name"):
            raise ValueError("Missing Fusion version/document evidence")
        if report.get("solid_count") != 1:
            raise ValueError("Expected one solid")
        dims = report.get("dimensions_mm")
        if not isinstance(dims, list) or len(dims) != 3:
            raise ValueError("Missing API dimension report")
        if any(not math.isfinite(v) or abs(v - target) > 0.01 for v, target in zip(dims, [10, 20, 5])):
            raise ValueError("API reported dimensions do not match the fixture")
        volume = report.get("volume_mm3", float("nan"))
        if not math.isfinite(volume) or abs(volume - 1000.0) > 0.1:
            raise ValueError("API reported volume does not match the fixture")
        hashes = {}
        for kind in ("step", "stl", "f3d"):
            path = run_dir / ("smoke." + kind)
            item = report.get("outputs", {}).get(kind, {})
            if not isinstance(item, dict):
                raise ValueError(f"Invalid output metadata: {kind}")
            if item.get("filename") != path.name:
                raise ValueError(f"Unexpected/missing output filename: {kind}")
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError(f"Missing/empty export: {kind}")
            actual_hash = sha256(path)
            if actual_hash != item.get("sha256") or path.stat().st_size != item.get("size_bytes"):
                raise ValueError(f"Export changed or metadata is inconsistent: {kind}")
            hashes[kind] = actual_hash
        if not (run_dir / "smoke.step").read_bytes()[:1024].lstrip().startswith(b"ISO-10303-21;"):
            raise ValueError("STEP header was not recognized")
        measured, count = stl_dimensions(run_dir / "smoke.stl")
        if any(abs(v - expected) > 0.01 for v, expected in zip(measured, [10, 20, 5])):
            raise ValueError(f"STL dimensions are {measured}; expected [10,20,5] in millimeters. No rescaling performed.")
        result.update(status="PASSED", dimensions_mm=measured, triangle_count=count,
                      export_sha256=hashes, report_sha256=sha256(run_dir / "fusion-report.json"))
    except (OSError, ValueError, TypeError, KeyError, struct.error) as exc:
        result["error"] = str(exc)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", type=Path, required=True)
    args = p.parse_args()
    if not args.run_dir.is_dir():
        p.error("--run-dir must be an existing smoke output directory")
    result = verify(args.run_dir)
    output = args.run_dir / "independent-verification.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASSED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
