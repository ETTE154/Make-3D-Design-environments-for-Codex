"""Run from Fusion Scripts and Add-Ins, never from a standalone Python process."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import traceback
import uuid
import adsk.core
import adsk.fusion


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    repo_root = Path(__file__).resolve().parents[2]
    output = repo_root / ".local" / "fusion-smoke" / run_id
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "run_id": run_id, "status": "RUNNING", "fusion_version": app.version,
        "source_script": str(Path(__file__).resolve()), "outputs": {},
        "print_ready": False, "mcp_verified": False,
    }
    try:
        # A new document leaves the user's original model untouched.
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError("The new active product is not a Fusion Design")
        root = design.rootComponent
        units = design.unitsManager
        length_cm = units.evaluateExpression("10 mm", "cm")
        width_cm = units.evaluateExpression("20 mm", "cm")
        sketch = root.sketches.add(root.xYConstructionPlane)
        sketch.name = "AgentSmoke_10x20_mm"
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(length_cm, width_cm, 0),
        )
        if sketch.profiles.count != 1:
            raise RuntimeError("Expected exactly one closed rectangle profile")
        feature = root.features.extrudeFeatures.addSimple(
            sketch.profiles.item(0), adsk.core.ValueInput.createByString("5 mm"),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        )
        body = feature.bodies.item(0)
        body.name = "AgentSmoke_10x20x5_mm"
        box = body.boundingBox
        dimensions = [
            (box.maxPoint.x - box.minPoint.x) * 10.0,
            (box.maxPoint.y - box.minPoint.y) * 10.0,
            (box.maxPoint.z - box.minPoint.z) * 10.0,
        ]
        volume = body.volume * 1000.0
        report.update(document_name=doc.name, dimensions_mm=dimensions,
                      volume_mm3=volume, solid_count=root.bRepBodies.count,
                      source_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        if root.bRepBodies.count != 1 or not body.isSolid:
            raise RuntimeError("Expected one solid body")
        if any(abs(a - b) > 1e-6 for a, b in zip(dimensions, [10.0, 20.0, 5.0])):
            raise RuntimeError("API dimension validation failed")
        if abs(volume - 1000.0) > 1e-3:
            raise RuntimeError("API volume validation failed")
        export = design.exportManager
        requests = [
            ("step", export.createSTEPExportOptions(str(output / "smoke.step"), root)),
            ("stl", export.createSTLExportOptions(body, str(output / "smoke.stl"))),
            ("f3d", export.createFusionArchiveExportOptions(str(output / "smoke.f3d"))),
        ]
        for kind, options in requests:
            if options is None or not export.execute(options):
                raise RuntimeError("Export returned failure: " + kind)
            path = output / ("smoke." + kind)
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError("Export file is missing or empty: " + kind)
            report["outputs"][kind] = {
                "filename": path.name, "size_bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        app.activeViewport.fit()
        report["status"] = "CAD_SMOKE_PASSED"
        report["next"] = "Run scripts/verify_smoke.py, reopen STEP/F3D, then inspect the real slicer profile."
    except Exception:
        report["status"] = "FAILED"
        report["traceback"] = traceback.format_exc()
    report_file = output / "fusion-report.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    ui.messageBox("AgentSmokeTest: " + report["status"] + "\nReport: " + str(report_file)
                  + "\nThis is not approval to start a 3D printer.")
