import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from purchasing_power.frozen_sources import FROZEN_COLUMNS, FROZEN_FILENAMES, load_frozen_sources


class FrozenSourceTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.directory = Path(self.workspace.name)
        files = {}
        for name, filename in FROZEN_FILENAMES.items():
            frame = pd.DataFrame([{column: "2018-01-01" if column == "month" else 1
                                   for column in FROZEN_COLUMNS[name]}])
            path = self.directory / filename
            frame.to_csv(path, index=False)
            files[name] = {"file": filename,
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                           "observations": len(frame)}
        (self.directory / "manifest.json").write_text(json.dumps({"format_version": 1,
                                                                    "files": files}), encoding="utf-8")

    def tearDown(self):
        self.workspace.cleanup()

    def test_loads_verified_schema_and_counts(self):
        frames, manifest = load_frozen_sources(self.directory)
        self.assertEqual(set(frames), set(FROZEN_FILENAMES))
        self.assertEqual(manifest["format_version"], 1)
        self.assertEqual(len(frames["cpi"]), 1)

    def test_checksum_mismatch_is_rejected(self):
        path = self.directory / FROZEN_FILENAMES["cpi"]
        path.write_bytes(path.read_bytes() + b"\nmodified")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            load_frozen_sources(self.directory)

    def test_unexpected_file_name_is_rejected(self):
        path = self.directory / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["files"]["cpi"]["file"] = "../outside.csv"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "filename"):
            load_frozen_sources(self.directory)

    def test_missing_dataset_is_rejected(self):
        path = self.directory / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        del manifest["files"]["ppp"]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "manifest"):
            load_frozen_sources(self.directory)


if __name__ == "__main__":
    unittest.main()
