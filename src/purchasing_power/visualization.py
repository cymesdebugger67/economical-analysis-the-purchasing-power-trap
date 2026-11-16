from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


COLORS = {"davao_region": "#175d73", "philippines": "#db8b29", "food_and_beverages": "#a44235",
          "housing_and_utilities": "#775b9b", "transport": "#438b65"}
SOURCE = "Source: PSA OpenSTAT (2018=100); NWPC wage orders where wages are shown."


def _finish(figure: plt.Figure, axes: plt.Axes, title: str, ylabel: str, path: Path,
            xlabel: str = "Month", source: str = SOURCE) -> None:
    axes.set_title(title, loc="left", fontsize=14, fontweight="bold", pad=16)
    axes.set_ylabel(ylabel)
    axes.set_xlabel(xlabel)
    if xlabel == "Month":
        axes.set_xlim(pd.Timestamp("2018-01-01"), pd.Timestamp("2025-12-01"))
    axes.grid(axis="y", alpha=0.2)
    axes.spines[["top", "right"]].set_visible(False)
    axes.margins(y=0.18)
    axes.legend(frameon=False, loc="upper left", ncol=2, fontsize=9)
    figure.text(0.075, 0.015, source, fontsize=8, color="#555555")
    figure.autofmt_xdate()
    figure.tight_layout(rect=(0, 0.04, 1, 1))
    figure.savefig(path, dpi=180, facecolor="white")
    plt.close(figure)


def generate_figures(cpi: pd.DataFrame, wages: pd.DataFrame, directory: Path,
                     fies: Optional[pd.DataFrame] = None) -> list[str]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    all_items = cpi.loc[cpi["commodity"] == "all_items"]
    figure, axes = plt.subplots(figsize=(11, 5))
    for geography, group in all_items.groupby("geography"):
        axes.plot(group["month"], group["cpi"], label=geography.replace("_", " ").title(),
                  color=COLORS[geography], linewidth=2.3)
    path = directory / "regional_and_national_cpi.png"
    _finish(figure, axes, "Consumer prices in Davao Region and the Philippines", "CPI (2018=100)", path)
    paths.append(str(path))

    baseline = wages.loc[wages["commodity"] == "all_items"]
    figure, axes = plt.subplots(figsize=(11, 5))
    axes.plot(baseline["month"], baseline["nominal_wage_php"], label="Nominal statutory wage",
              color=COLORS["davao_region"], linewidth=2.3)
    axes.plot(baseline["month"], baseline["real_wage_2018_php"], label="Real statutory wage (2018 pesos)",
              color=COLORS["philippines"], linewidth=2.3)
    path = directory / "nominal_and_real_statutory_wages.png"
    _finish(figure, axes, "Region XI statutory daily wage and its real value", "PHP per day", path)
    paths.append(str(path))

    figure, axes = plt.subplots(figsize=(11, 5))
    axes.plot(baseline["month"], baseline["indexed_nominal_wage"], label="Statutory wage",
              color=COLORS["davao_region"], linewidth=2.3)
    axes.plot(baseline["month"], baseline["indexed_cpi"], label="All-items CPI",
              color=COLORS["philippines"], linewidth=2.3)
    path = directory / "indexed_wage_and_prices.png"
    _finish(figure, axes, "Wage adjustments against Davao consumer prices", "January 2018=100", path)
    paths.append(str(path))

    figure, axes = plt.subplots(figsize=(11, 5))
    regional = cpi.loc[cpi["geography"] == "davao_region"]
    for commodity, group in regional.groupby("commodity"):
        axes.plot(group["month"], group["cpi"], label=commodity.replace("_", " ").title(),
                  color=COLORS.get(commodity, COLORS["davao_region"]), linewidth=2)
    path = directory / "essential_commodity_cpi.png"
    _finish(figure, axes, "Selected Davao commodity price indices", "CPI (2018=100)", path)
    paths.append(str(path))

    figure, axes = plt.subplots(figsize=(11, 5))
    axes.plot(baseline["month"], baseline["real_wage_2018_php"], label="Month-end wage, all-items CPI",
              color=COLORS["davao_region"], linewidth=2.2)
    axes.plot(baseline["month"], baseline["day_weighted_real_wage_2018_php"],
              label="Calendar-day weighted wage, all-items CPI", color=COLORS["philippines"], linewidth=1.5)
    food = wages.loc[wages["commodity"] == "food_and_beverages"]
    axes.plot(food["month"], food["real_wage_2018_php"], label="Month-end wage, food CPI",
              color=COLORS["food_and_beverages"], linewidth=1.8)
    path = directory / "wage_sensitivity_comparison.png"
    _finish(figure, axes, "Real wage sensitivity to timing and deflator", "2018 PHP per day", path)
    paths.append(str(path))

    figure, axes = plt.subplots(figsize=(11, 5))
    baseline_real = float(baseline["real_wage_2018_php"].iloc[0])
    axes.plot(baseline["month"], baseline["real_wage_2018_php"], label="Real statutory wage",
              color=COLORS["davao_region"], linewidth=2.3)
    axes.axhline(baseline_real, color="#626b73", linewidth=1.5, linestyle="--", label="January 2018 reference")
    axes.fill_between(baseline["month"], baseline["real_wage_2018_php"], baseline_real,
                      where=baseline["real_wage_2018_php"] < baseline_real,
                      color=COLORS["food_and_beverages"], alpha=0.28, label="Below reference")
    below = baseline.loc[baseline["real_wage_2018_php"] < baseline_real]
    axes.scatter(below["month"], below["real_wage_2018_php"], s=22,
                 color=COLORS["food_and_beverages"], zorder=4)
    changes = baseline.loc[baseline["nominal_wage_php"].diff().fillna(0) > 0]
    axes.scatter(changes["month"], changes["real_wage_2018_php"], marker="o", s=28,
                 color=COLORS["philippines"], label="Wage-order month", zorder=4)
    path = directory / "real_wage_below_reference.png"
    _finish(figure, axes, "Real wage path and below-reference episodes", "2018 PHP per day", path)
    paths.append(str(path))

    if fies is not None:
        regional_fies = fies.loc[(fies["geography"] == "davao_region") &
                                  (fies["income_decile"] > 0)]
        figure, axes = plt.subplots(figsize=(11, 5))
        for category, label, color in (("food_and_beverages", "Food and beverages", COLORS["food_and_beverages"]),
                                       ("housing_and_utilities", "Housing and utilities", COLORS["housing_and_utilities"]),
                                       ("transport", "Transport", COLORS["transport"])):
            selected = regional_fies.loc[regional_fies["category"] == category].sort_values("income_decile")
            axes.plot(selected["income_decile"], selected["value"], marker="o", linewidth=2.2,
                      markersize=4, label=label, color=color)
        axes.set_xticks(range(1, 11))
        path = directory / "fies_expenditure_shares_by_decile.png"
        _finish(figure, axes, "Davao expenditure composition across income deciles, 2023",
                "Share of group expenditure (%)", path, xlabel="Per-capita-income decile",
                source="Source: PSA 2023 FIES, OpenSTAT Table 7. Shares are cross-sectional, not inflation rates.")
        paths.append(str(path))

        region_food = fies.loc[(fies["category"] == "food_and_beverages") &
                               (fies["income_decile"].between(1, 10))]
        figure, axes = plt.subplots(figsize=(11, 5))
        for geography, label in (("davao_region", "Davao Region"), ("philippines", "Philippines")):
            values = region_food.loc[region_food["geography"] == geography].sort_values("income_decile")
            axes.plot(values["income_decile"], values["value"], marker="o", markersize=4,
                      linewidth=2.2, label=label, color=COLORS[geography])
        axes.set_xticks(range(1, 11))
        path = directory / "fies_food_share_davao_vs_philippines.png"
        _finish(figure, axes, "Food share of family expenditure by income decile, 2023",
                "Food share of total family expenditure (%)", path,
                xlabel="Per-capita-income decile",
                source="Source: PSA 2023 FIES, OpenSTAT Table 7. Descriptive shares, not inflation rates.")
        paths.append(str(path))
    return paths


def generate_contact_sheet(figure_paths: list[Path], output_path: Path) -> Path:
    columns = 2
    rows = (len(figure_paths) + columns - 1) // columns
    figure, axes = plt.subplots(rows, columns, figsize=(18, rows * 5.2))
    for axes_item, path in zip(axes.flat, figure_paths):
        axes_item.imshow(plt.imread(path))
        axes_item.set_title(path.stem.replace("_", " ").title(), loc="left", fontsize=11, pad=6)
        axes_item.axis("off")
    for axes_item in list(axes.flat)[len(figure_paths):]:
        axes_item.axis("off")
    figure.tight_layout()
    figure.savefig(output_path, dpi=150, facecolor="white")
    plt.close(figure)
    return output_path
