"""Synthetic STL/report fixtures only; these tests do not invoke Autodesk Fusion."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("verifier", Path(__file__).resolve().parents[1] / "scripts/verify_smoke.py")
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def box_stl(scale=1.0, binary=True):
    vertices = [(0,0,0),(10,0,0),(10,20,0),(0,20,0),(0,0,5),(10,0,5),(10,20,5),(0,20,5)]
    faces = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    if binary:
        result = b"TEST ONLY".ljust(80, b" ") + struct.pack("<I",len(faces))
        for face in faces:
            xyz = [v*scale for i in face for v in vertices[i]]
            result += struct.pack("<12fH", 0,0,0,*xyz,0)
        return result
    rows = ["solid test"]
    for face in faces:
        rows += ["facet normal 0 0 0", "outer loop"]
        rows += ["vertex " + " ".join(str(v*scale) for v in vertices[i]) for i in face]
        rows += ["endloop", "endfacet"]
    rows += ["endsolid test"]
    return "\n".join(rows).encode("ascii")


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "test-run"
        self.root.mkdir()

    def fixture(self, scale=1, binary=True):
        (self.root / "smoke.stl").write_bytes(box_stl(scale,binary))
        (self.root / "smoke.step").write_text("ISO-10303-21;\nTEST FIXTURE ONLY")
        (self.root / "smoke.f3d").write_bytes(b"F3D TEST FIXTURE: not a real Fusion archive")
        report = {"run_id":"test-run", "status":"CAD_SMOKE_PASSED", "fusion_version":"TEST_ONLY",
                  "document_name":"TEST_ONLY", "dimensions_mm":[10,20,5], "solid_count":1,
                  "volume_mm3":1000, "outputs":{}}
        for kind in ("stl","step","f3d"):
            p = self.root / ("smoke."+kind)
            report["outputs"][kind] = {"filename":p.name, "size_bytes":p.stat().st_size,
                                        "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
        self.save(report)
        return report

    def save(self, report):
        (self.root / "fusion-report.json").write_text(json.dumps(report))

    def test_binary_dimensions(self):
        self.fixture()
        result = verifier.verify(self.root)
        self.assertEqual(result["status"],"PASSED")
        self.assertEqual(result["dimensions_mm"],[10,20,5])
        self.assertFalse(result["print_ready"])

    def test_ascii_dimensions(self):
        self.fixture(binary=False)
        self.assertEqual(verifier.verify(self.root)["status"],"PASSED")

    def test_unit_factor_ten_fails(self):
        self.fixture(scale=10)
        self.assertEqual(verifier.verify(self.root)["status"],"FAILED")

    def test_small_unit_factor_fails(self):
        self.fixture(scale=0.1)
        self.assertEqual(verifier.verify(self.root)["status"],"FAILED")

    def test_modified_file_fails(self):
        self.fixture()
        with (self.root / "smoke.stl").open("ab") as f:
            f.write(b"tampered")
        self.assertEqual(verifier.verify(self.root)["status"],"FAILED")

    def test_failed_cad_report(self):
        report=self.fixture(); report["status"]="FAILED"; self.save(report)
        self.assertEqual(verifier.verify(self.root)["status"],"FAILED")

    def test_stale_run_id(self):
        report=self.fixture(); report["run_id"]="old-run"; self.save(report)
        self.assertEqual(verifier.verify(self.root)["status"],"FAILED")

    def test_wrong_volume(self):
        report=self.fixture(); report["volume_mm3"]=10; self.save(report)
        self.assertEqual(verifier.verify(self.root)["status"],"FAILED")

    def test_nonfinite_coordinates(self):
        p=self.root / "nan.stl"
        p.write_bytes(box_stl(float("nan")))
        with self.assertRaises(ValueError):
            verifier.stl_dimensions(p)

    def test_empty_stl(self):
        p=self.root / "empty.stl"; p.write_bytes(b"solid empty\nendsolid empty")
        with self.assertRaises(ValueError):
            verifier.stl_dimensions(p)

    def test_malformed_json(self):
        self.fixture(); (self.root / "fusion-report.json").write_text("{")
        self.assertEqual(verifier.verify(self.root)["status"],"FAILED")


if __name__ == "__main__":
    unittest.main()
