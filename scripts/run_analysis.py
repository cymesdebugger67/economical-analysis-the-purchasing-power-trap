import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from purchasing_power.analysis import calculate_cpi_metrics, calculate_wage_metrics, monthly_wage_rates
from purchasing_power.frozen_sources import load_frozen_sources
from purchasing_power.household_expenditure import prepare_fies, summarize_fies, validate_fies
from purchasing_power.preparation import load_pxweb_records, load_wage_events, prepare_monthly_series
from purchasing_power.sources import acquire_fies, acquire_official_sources, acquire_wage_order_documents, file_sha256
from purchasing_power.temporal_analysis import below_reference_episodes, endpoint_decomposition, peak_to_trough_drawdown, wage_event_windows
from purchasing_power.validation import EXPECTED_MONTHS, validate_base_year, validate_monthly_series, validate_ppp_reconciliation, validate_wage_event_audit, validate_wage_events
from purchasing_power.visualization import generate_contact_sheet, generate_figures


def load_captured_sources(raw: Path) -> tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame], dict]:
    manifest = json.loads((raw / "source_manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["sources"].values():
        if file_sha256(raw / entry["file"]) != entry["sha256"]:
            raise ValueError(f"Raw source checksum mismatch: {entry['file']}")
    cpi = prepare_monthly_series(load_pxweb_records(raw / "psa_cpi_2018_2025.json"), is_cpi=True)
    ppp = prepare_monthly_series(load_pxweb_records(raw / "psa_ppp_2018_2025.json"), is_cpi=False)
    source_hashes = {name: entry["sha256"] for name, entry in manifest["sources"].items()}
    details = {"reproduction_mode": "captured", "source_hashes": source_hashes}
    fies = None
    fies_path = raw / "fies_manifest.json"
    if fies_path.exists():
        fies_manifest = json.loads(fies_path.read_text(encoding="utf-8"))
        if file_sha256(raw / fies_manifest["file"]) != fies_manifest["sha256"]:
            raise ValueError("FIES captured source checksum mismatch")
        fies = prepare_fies(load_pxweb_records(raw / fies_manifest["file"]))
        details["source_hashes"]["fies"] = fies_manifest["sha256"]
    wage_order_manifest = raw / "wage_orders" / "manifest.json"
    if wage_order_manifest.exists():
        original_orders = json.loads(wage_order_manifest.read_text(encoding="utf-8"))
        for order, entry in original_orders["orders"].items():
            if file_sha256(raw / "wage_orders" / entry["file"]) != entry["sha256"]:
                raise ValueError(f"Original wage order {order} checksum mismatch")
        details["original_wage_order_hashes"] = {
            order: entry["sha256"] for order, entry in original_orders["orders"].items()
        }
    return cpi, ppp, fies, details


def load_reproducible_snapshot(directory: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    frames, manifest = load_frozen_sources(directory)
    details = {
        "reproduction_mode": "frozen",
        "source_hashes": {name: entry["source_sha256"] for name, entry in manifest["files"].items()},
        "frozen_input_hashes": {name: entry["sha256"] for name, entry in manifest["files"].items()},
        "source_retrieved_on": manifest["source_retrieved_on"],
    }
    return frames["cpi"], frames["ppp"], frames["fies"], details


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible Davao statutory-wage and CPI case study")
    parser.add_argument("--source", choices=("auto", "captured", "frozen"), default="auto",
                        help="auto uses captured source files if present, otherwise the tracked frozen snapshot")
    parser.add_argument("--acquire", action="store_true", help="Download sources only if no captured vintage exists")
    parser.add_argument("--acquire-fies", action="store_true", help="Retrieve 2023 FIES into the captured vintage")
    parser.add_argument("--refresh-vintage", action="store_true", help="Acquire a separate timestamped source vintage")
    args = parser.parse_args()
    if args.source == "frozen" and (args.acquire or args.acquire_fies or args.refresh_vintage):
        parser.error("Frozen source replay cannot be combined with acquisition")
    if args.refresh_vintage and (args.acquire or args.acquire_fies):
        parser.error("--refresh-vintage cannot be combined with other acquisition flags")
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    output_root = root / "reports"
    processed = root / "data" / "processed"
    if args.refresh_vintage:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        raw = raw / "vintages" / stamp
        output_root = output_root / "vintages" / stamp
        processed = processed / "vintages" / stamp
        acquire_official_sources(raw)
        acquire_fies(raw)
        acquire_wage_order_documents(raw)
    elif args.acquire:
        acquire_official_sources(raw)
        acquire_fies(raw)
        acquire_wage_order_documents(raw)
    elif args.acquire_fies:
        if not (raw / "source_manifest.json").exists():
            parser.error("Acquire CPI and PPP first using --acquire")
        acquire_fies(raw)
    capture_exists = (raw / "source_manifest.json").exists()
    source_mode = "captured" if args.refresh_vintage or args.acquire or args.acquire_fies else (
        "captured" if args.source == "auto" and capture_exists else
        "frozen" if args.source == "auto" else args.source
    )
    if source_mode == "captured":
        cpi, ppp, fies, source_details = load_captured_sources(raw)
    else:
        cpi, ppp, fies, source_details = load_reproducible_snapshot(root / "data" / "frozen")
    events = load_wage_events(root / "data" / "reference" / "region_xi_wage_events.csv")
    event_audit = pd.read_csv(root / "data" / "reference" / "region_xi_wage_event_audit.csv",
                              parse_dates=["effective_date"])
    diagnostics = {
        **source_details,
        "cpi": validate_monthly_series(cpi, ["geography", "commodity"], "cpi", 8),
        "ppp": validate_monthly_series(ppp, ["geography"], "official_ppp", 2),
        "wages": validate_wage_events(events),
        "wage_event_audit": validate_wage_event_audit(events, event_audit),
        "base_year": validate_base_year(cpi),
        "ppp_reconciliation": validate_ppp_reconciliation(cpi, ppp),
    }
    if fies is not None:
        diagnostics["fies"] = validate_fies(fies)
    cpi_metrics = calculate_cpi_metrics(cpi)
    wage_rates = monthly_wage_rates(events, EXPECTED_MONTHS)
    wage_metrics = calculate_wage_metrics(cpi_metrics, wage_rates)
    tables = output_root / "tables"
    processed.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    cpi_metrics.to_csv(processed / "monthly_cpi_metrics.csv", index=False, float_format="%.8f")
    wage_metrics.to_csv(processed / "monthly_wage_metrics.csv", index=False, float_format="%.8f")
    if fies is not None:
        fies.to_csv(processed / "fies_2023_selected_observations.csv", index=False, float_format="%.4f")
        summarize_fies(fies).to_csv(tables / "fies_decile_composition_2023.csv", index=False,
                                    float_format="%.4f")
    (tables / "validation_diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    all_items = wage_metrics.loc[wage_metrics["commodity"] == "all_items"].set_index("month")
    summary = all_items.loc[[pd.Timestamp("2018-01-01"), pd.Timestamp("2025-12-01")],
                            ["nominal_wage_php", "cpi", "real_wage_2018_php", "real_wage_change_percent"]]
    summary.to_csv(tables / "headline_summary.csv", float_format="%.4f")
    commodity = wage_metrics.loc[wage_metrics["month"] == pd.Timestamp("2025-12-01"),
                                 ["commodity", "cpi", "cumulative_change_percent", "real_wage_2018_php"]]
    commodity.to_csv(tables / "commodity_summary_december_2025.csv", index=False, float_format="%.4f")
    episodes = below_reference_episodes(wage_metrics)
    episodes.to_csv(tables / "below_reference_episodes.csv", index=False, float_format="%.4f")
    wage_event_windows(wage_metrics, events).to_csv(tables / "wage_event_windows.csv", index=False,
                                                   float_format="%.4f")
    decomposition = endpoint_decomposition(wage_metrics, cpi_metrics)
    temporal_summary = {
        "months_below_reference": int(episodes["months"].sum()),
        "longest_episode_months": int(episodes["months"].max()) if not episodes.empty else 0,
        "maximum_drawdown": peak_to_trough_drawdown(wage_metrics),
        "endpoint_decomposition": decomposition,
    }
    (tables / "temporal_summary.json").write_text(json.dumps(temporal_summary, indent=2), encoding="utf-8")
    paths = generate_figures(cpi_metrics, wage_metrics, output_root / "figures", fies=fies)
    contact_sheet = generate_contact_sheet([Path(path) for path in paths], output_root / "figures" /
                                           "visual_review_contact_sheet.png")
    print(json.dumps({"validation": diagnostics, "figures": paths, "contact_sheet": str(contact_sheet),
                      "temporal_summary": temporal_summary,
                      "headline_summary": summary.reset_index().assign(
                          month=lambda frame: frame["month"].dt.strftime("%Y-%m")).to_dict("records")}, indent=2))


if __name__ == "__main__":
    main()
