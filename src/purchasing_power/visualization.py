from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


COLORS = {"davao_region": "#175d73", "philippines": "#db8b29", "food_and_beverages": "#a44235",
          "housing_and_utilities": "#775b9b", "transport": "#438b65"}
SOURCE = "Source: PSA OpenSTAT (2018=100); NWPC wage orders where wages are shown."


def _finish(figure: plt.Figure, axes: plt.Axes, title: str, ylabel: str, path: Path) -> None:
    axes.set_title(title, loc="left", fontsize=14, fontweight="bold", pad=16)
    axes.set_ylabel(ylabel)
    axes.set_xlabel("Month")
    axes.grid(axis="y", alpha=0.2)
    axes.spines[["top", "right"]].set_visible(False)
    axes.margins(y=0.18)
    axes.legend(frameon=False, loc="upper left", ncol=2, fontsize=9)
    figure.text(0.075, 0.015, SOURCE, fontsize=8, color="#555555")
    figure.autofmt_xdate()
    figure.tight_layout(rect=(0, 0.04, 1, 1))
    figure.savefig(path, dpi=180, facecolor="white")
    plt.close(figure)


def generate_figures(cpi: pd.DataFrame, wages: pd.DataFrame, directory: Path) -> list[str]:
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
    return paths
