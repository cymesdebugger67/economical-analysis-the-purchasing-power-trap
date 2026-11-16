import json
from pathlib import Path
import re
import subprocess
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from purchasing_power.frozen_sources import load_frozen_sources


FIGURES = (
    "regional_and_national_cpi.png",
    "nominal_and_real_statutory_wages.png",
    "indexed_wage_and_prices.png",
    "essential_commodity_cpi.png",
    "wage_sensitivity_comparison.png",
    "real_wage_below_reference.png",
    "fies_expenditure_shares_by_decile.png",
    "fies_food_share_davao_vs_philippines.png",
    "visual_review_contact_sheet.png",
)


def verify_release(root: Path) -> dict:
    frames, manifest = load_frozen_sources(root / "data" / "frozen")
    figures = root / "reports" / "figures"
    for filename in FIGURES:
        path = figures / filename
        if not path.exists() or path.stat().st_size < 1000 or path.open("rb").read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Missing or malformed figure: {filename}")
    readme = (root / "README.md").read_text(encoding="utf-8")
    for link in re.findall(r"\]\(([^)]+)\)", readme):
        if link.startswith(("https://", "http://", "mailto:")) or link.startswith("#"):
            continue
        target = (root / link.split("#", 1)[0]).resolve()
        if not target.is_relative_to(root.resolve()) or not target.exists():
            raise ValueError(f"README local link target is missing: {link}")
    headline = pd.read_csv(root / "reports" / "tables" / "headline_summary.csv")
    if len(headline) != 2 or list(headline["month"]) != ["2018-01-01", "2025-12-01"]:
        raise ValueError("Headline summary does not match study endpoints")
    change = float(headline["real_wage_change_percent"].iloc[-1])
    if not 11.18 < change < 11.20:
        raise ValueError("Headline results differ from the documented frozen baseline")
    diagnostics = json.loads((root / "reports" / "tables" / "validation_diagnostics.json").read_text())
    if diagnostics["cpi"]["rows"] != 768 or diagnostics["ppp"]["rows"] != 192:
        raise ValueError("Monthly output diagnostics are incomplete")
    if diagnostics["fies"]["rows"] != 176:
        raise ValueError("FIES output diagnostics are incomplete")
    notebook = json.loads((root / "notebooks" / "purchasing_power_analysis.ipynb").read_text())
    if notebook["nbformat"] != 4 or not notebook["cells"]:
        raise ValueError("Notebook format is malformed")
    git_result = subprocess.run(["git", "ls-files", "data/raw", ".venv", ".venv_clean"],
                                cwd=root, capture_output=True, text=True, check=False)
    if git_result.returncode == 0 and git_result.stdout.strip():
        raise ValueError("Ignored source files or virtual environments are tracked by Git")
    return {"status": "passed", "frozen_input_rows": {k: len(v) for k, v in frames.items()},
            "manifest_version": manifest["format_version"], "figures_checked": len(FIGURES),
            "readme_links": len(re.findall(r"\]\(([^)]+)\)", readme)),
            "headline_endpoint_real_wage_change_percent": change}


if __name__ == "__main__":
    print(json.dumps(verify_release(Path(__file__).resolve().parents[1]), indent=2))
