import json
from pathlib import Path

import pandas as pd

from purchasing_power.sources import file_sha256


FROZEN_FILENAMES = {
    "cpi": "monthly_cpi_2018_2025.csv",
    "ppp": "monthly_purchasing_power_2018_2025.csv",
    "fies": "fies_expenditure_2023.csv",
}
FROZEN_COLUMNS = {
    "cpi": ["month", "geography", "commodity", "cpi"],
    "ppp": ["month", "geography", "official_ppp"],
    "fies": ["geography", "income_decile", "category", "value", "unit"],
}


def load_frozen_sources(directory: Path) -> tuple[dict[str, pd.DataFrame], dict]:
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format_version") != 1 or set(manifest.get("files", {})) != set(FROZEN_FILENAMES):
        raise ValueError("Frozen source manifest has an unexpected format or missing datasets")
    frames = {}
    for source, expected_filename in FROZEN_FILENAMES.items():
        entry = manifest["files"][source]
        if entry.get("file") != expected_filename:
            raise ValueError(f"Frozen {source} filename does not match the declared contract")
        path = directory / expected_filename
        if file_sha256(path) != entry["sha256"]:
            raise ValueError(f"Frozen {source} SHA-256 checksum mismatch")
        options = {"parse_dates": ["month"]} if source != "fies" else {"dtype": {"income_decile": int}}
        frame = pd.read_csv(path, **options)
        if list(frame.columns) != FROZEN_COLUMNS[source]:
            raise ValueError(f"Frozen {source} data schema mismatch")
        if len(frame) != entry["observations"]:
            raise ValueError(f"Frozen {source} observation count mismatch")
        frames[source] = frame
    return frames, manifest
