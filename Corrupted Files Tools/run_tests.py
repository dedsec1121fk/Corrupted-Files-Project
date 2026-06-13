#!/usr/bin/env python3
"""Run dependency-free smoke tests for the archive and reader."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from corrupted_files_core import (  # noqa: E402
    audit_project,
    decode_escaped_unicode,
    load_database,
    normalize_text,
)


def load_reader_module():
    path = ROOT / "Corrupted Files.py"
    spec = importlib.util.spec_from_file_location("corrupted_files_reader", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not import Corrupted Files.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.database = load_database(ROOT, strict=True)
        cls.reader = load_reader_module()

    def test_database_has_unique_records(self) -> None:
        ids = [entry["id"] for entry in self.database.entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 443)

    def test_unicode_escape_decoder(self) -> None:
        self.assertEqual(decode_escaped_unicode("A#U2014B#U2013C"), "A—B–C")
        self.assertEqual(decode_escaped_unicode("#U00D6calan"), "Öcalan")

    def test_accent_insensitive_normalization(self) -> None:
        self.assertEqual(normalize_text("Ελλάδα"), normalize_text("ΕΛΛΑΔΑ"))
        self.assertEqual(normalize_text("Öcalan"), normalize_text("Ocalan"))

    def test_structural_audit_passes(self) -> None:
        report = audit_project(ROOT)
        self.assertTrue(report["ok"], report["errors"][:10])
        self.assertEqual(report["metrics"]["missing_media_references"], 0)
        self.assertEqual(report["metrics"]["path_mismatches"], 0)

    def test_ranked_search(self) -> None:
        results = self.reader.cli_search(self.database.entries, "watergate country:usa", "en", 10)
        self.assertTrue(results)
        self.assertIn("watergate", normalize_text(results[0]["title"]["en"]))

    def test_filter_search(self) -> None:
        results = self.reader.filter_entries(self.database.entries, country="Greece", year_text="2023")
        self.assertTrue(results)
        self.assertTrue(all(self.reader.detect_country(entry) == "Greece" for entry in results))
        self.assertTrue(all(int(entry["year"]) == 2023 for entry in results))

    def test_visual_dashboards_and_manifest_exist(self) -> None:
        self.assertTrue((ROOT / "00 - Project Dashboard.svg").is_file())
        self.assertTrue((ROOT / "Greece" / "00 - Country Dashboard.svg").is_file())
        self.assertTrue((ROOT / "USA" / "00 - Country Dashboard.svg").is_file())
        manifest_path = ROOT / "00 - Media Manifest.json"
        self.assertTrue(manifest_path.is_file())
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload), 443)
        self.assertTrue(any(item.get("has_generated_snapshot") for item in payload))

    def test_event_image_attribution_is_complete(self) -> None:
        manifest_path = ROOT / "00 - Event Image Attribution.json"
        self.assertTrue(manifest_path.is_file())
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload), 9)
        self.assertTrue(all(item.get("rights_status") == "verified" for item in payload))
        tracked = {item["file"] for item in payload}
        actual = {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*Event Image*")
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        }
        self.assertEqual(tracked, actual)


class CliSmokeTests(unittest.TestCase):
    def test_stats_cli_returns_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "Corrupted Files.py"), "--stats"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=30,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["records"], 443)
        self.assertEqual(payload["media_references"], 981)


if __name__ == "__main__":
    unittest.main(verbosity=2)
