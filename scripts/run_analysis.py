import argparse
import json
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from purchasing_power.analysis import calculate_cpi_metrics, calculate_wage_metrics, monthly_wage_rates
from purchasing_power.preparation import load_pxweb_records, load_wage_events, prepare_monthly_series
from purchasing_power.sources import acquire_official_sources, file_sha256
from purchasing_power.validation import EXPECTED_MONTHS, validate_base_year, validate_monthly_series, validate_ppp_reconciliation, validate_wage_events
from purchasing_power.visualization import generate_figures


def main() -> None:
    parser = argparse.ArgumentParser(description="Run validated Davao statutory wage and CPI analysis")
    parser.add_argument("--acquire", action="store_true", help="Refresh Git-ignored official raw source files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw"
    if args.acquire:
        acquire_official_sources(raw)
    manifest = json.loads((raw / "source_manifest.json").read_text(encoding="utf-8"))
    for source in manifest["sources"].values():
        if file_sha256(raw / source["file"]) != source["sha256"]:
            raise ValueError(f"Raw source checksum mismatch: {source['file']}")
    cpi = prepare_monthly_series(load_pxweb_records(raw / "psa_cpi_2018_2025.json"), is_cpi=True)
    ppp = prepare_monthly_series(load_pxweb_records(raw / "psa_ppp_2018_2025.json"), is_cpi=False)
    events = load_wage_events(root / "data" / "reference" / "region_xi_wage_events.csv")
    diagnostics = {
        "cpi": validate_monthly_series(cpi, ["geography", "commodity"], "cpi", 8),
        "ppp": validate_monthly_series(ppp, ["geography"], "official_ppp", 2),
        "wages": validate_wage_events(events),
        "base_year": validate_base_year(cpi),
        "ppp_reconciliation": validate_ppp_reconciliation(cpi, ppp),
        "source_hashes": {name: entry["sha256"] for name, entry in manifest["sources"].items()},
    }
    cpi_metrics = calculate_cpi_metrics(cpi)
    wage_rates = monthly_wage_rates(events, EXPECTED_MONTHS)
    wage_metrics = calculate_wage_metrics(cpi_metrics, wage_rates)
    processed = root / "data" / "processed"
    tables = root / "reports" / "tables"
    processed.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    cpi_metrics.to_csv(processed / "monthly_cpi_metrics.csv", index=False, float_format="%.8f")
    wage_metrics.to_csv(processed / "monthly_wage_metrics.csv", index=False, float_format="%.8f")
    (tables / "validation_diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    all_items = wage_metrics.loc[wage_metrics["commodity"] == "all_items"].set_index("month")
    summary = all_items.loc[[pd.Timestamp("2018-01-01"), pd.Timestamp("2025-12-01")],
                            ["nominal_wage_php", "cpi", "real_wage_2018_php", "real_wage_change_percent"]]
    summary.to_csv(tables / "headline_summary.csv", float_format="%.4f")
    commodity = wage_metrics.loc[wage_metrics["month"] == pd.Timestamp("2025-12-01"),
                                 ["commodity", "cpi", "cumulative_change_percent", "real_wage_2018_php"]]
    commodity.to_csv(tables / "commodity_summary_december_2025.csv", index=False, float_format="%.4f")
    paths = generate_figures(cpi_metrics, wage_metrics, root / "reports" / "figures")
    print(json.dumps({"validation": diagnostics, "figures": paths,
                      "headline_summary": summary.reset_index().assign(month=lambda frame: frame["month"].dt.strftime("%Y-%m")).to_dict("records")}, indent=2))


if __name__ == "__main__":
    main()
