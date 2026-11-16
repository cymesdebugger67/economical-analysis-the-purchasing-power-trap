import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from purchasing_power.frozen_sources import FROZEN_FILENAMES, load_frozen_sources
from purchasing_power.household_expenditure import prepare_fies, validate_fies
from purchasing_power.preparation import load_pxweb_records, prepare_monthly_series
from purchasing_power.sources import file_sha256
from purchasing_power.validation import validate_base_year, validate_monthly_series, validate_ppp_reconciliation


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze validated narrow source extracts for offline reproduction")
    parser.add_argument("--replace", action="store_true", help="Explicitly replace the existing frozen snapshot")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    destination = root / "data" / "frozen"
    manifest_path = destination / "manifest.json"
    if manifest_path.exists() and not args.replace:
        parser.error("Frozen manifest already exists; use --replace only after reviewing source changes")
    original_manifest = json.loads((raw / "source_manifest.json").read_text(encoding="utf-8"))
    original_fies_manifest = json.loads((raw / "fies_manifest.json").read_text(encoding="utf-8"))
    for entry in original_manifest["sources"].values():
        if file_sha256(raw / entry["file"]) != entry["sha256"]:
            raise ValueError(f"Raw source checksum mismatch: {entry['file']}")
    if file_sha256(raw / original_fies_manifest["file"]) != original_fies_manifest["sha256"]:
        raise ValueError("FIES raw source checksum mismatch")
    cpi = prepare_monthly_series(load_pxweb_records(raw / "psa_cpi_2018_2025.json"), is_cpi=True)
    ppp = prepare_monthly_series(load_pxweb_records(raw / "psa_ppp_2018_2025.json"), is_cpi=False)
    fies = prepare_fies(load_pxweb_records(raw / "psa_fies_2023_expenditure.json"))
    validate_monthly_series(cpi, ["geography", "commodity"], "cpi", 8)
    validate_monthly_series(ppp, ["geography"], "official_ppp", 2)
    validate_base_year(cpi)
    validate_ppp_reconciliation(cpi, ppp)
    validate_fies(fies)
    datasets = {
        "cpi": cpi.sort_values(["geography", "commodity", "month"]),
        "ppp": ppp.sort_values(["geography", "month"]),
        "fies": fies.sort_values(["geography", "income_decile", "category"]),
    }
    manifest = {
        "format_version": 1,
        "provenance": "Selected official observations; normalization checked against captured PSA extracts, not simulated data",
        "source_retrieved_on": original_manifest["retrieved_on"],
        "files": {},
    }
    destination.mkdir(parents=True, exist_ok=True)
    sources = {"cpi": original_manifest["sources"]["cpi"],
               "ppp": original_manifest["sources"]["ppp"], "fies": original_fies_manifest}
    for name, frame in datasets.items():
        path = destination / FROZEN_FILENAMES[name]
        frame.to_csv(path, index=False, float_format="%.8f", lineterminator="\n")
        manifest["files"][name] = {
            "file": path.name,
            "sha256": file_sha256(path),
            "observations": len(frame),
            "official_url": sources[name]["url"],
            "source_sha256": sources[name]["sha256"],
        }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    load_frozen_sources(destination)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
