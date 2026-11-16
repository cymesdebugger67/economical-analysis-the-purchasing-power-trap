import re

import pandas as pd

from purchasing_power.sources import FIES_CATEGORIES


GEOGRAPHY_LABELS = {"PHILIPPINES": "philippines", "REGION XI - DAVAO REGION": "davao_region"}
CATEGORY_LABELS = {
    "Total Family Expenditure (in millions)": "total_expenditure_million_php",
    "Food and Non-Alcoholic Beverages": "food_and_beverages",
    "Clothing and Footwear": "clothing_and_footwear",
    "Housing, Water, Electricity, Gas and Other Fuels": "housing_and_utilities",
    "Health": "health",
    "Transport": "transport",
    "Information and Communication": "information_and_communication",
    "Education": "education",
}
ESSENTIAL_CATEGORIES = ("food_and_beverages", "housing_and_utilities", "transport")


def prepare_fies(records: pd.DataFrame) -> pd.DataFrame:
    frame = records.copy()
    if set(frame["Region, Province, and HUC"]) != set(GEOGRAPHY_LABELS):
        raise ValueError("FIES extract contains unexpected geography")
    if set(frame["Major Expenditure Group"]) != set(FIES_CATEGORIES):
        raise ValueError("FIES extract contains unexpected category or hierarchy")
    expected_groups = {"All Income Groups"} | {f"{rank}{suffix} Decile" for rank, suffix in
                                             ((1, "st"), (2, "nd"), (3, "rd"), (4, "th"), (5, "th"),
                                              (6, "th"), (7, "th"), (8, "th"), (9, "th"), (10, "th"))}
    if set(frame["Indicator"]) != expected_groups:
        raise ValueError("FIES extract contains unexpected income decile")
    frame["geography"] = frame["Region, Province, and HUC"].map(GEOGRAPHY_LABELS)
    frame["category"] = frame["Major Expenditure Group"].map(CATEGORY_LABELS)
    frame["income_decile"] = frame["Indicator"].map(lambda value: 0 if value == "All Income Groups" else
                                                      int(re.match(r"\d+", value).group()))
    frame["value"] = pd.to_numeric(frame["value"], errors="raise")
    frame["unit"] = frame["category"].map(lambda value: "million_php" if value == "total_expenditure_million_php"
                                          else "percent_of_group_expenditure")
    return frame[["geography", "income_decile", "category", "value", "unit"]]


def validate_fies(frame: pd.DataFrame, tolerance_percentage_points: float = 0.15) -> dict:
    if frame.empty or frame.isna().any().any():
        raise ValueError("FIES contains missing values")
    if frame.duplicated(["geography", "income_decile", "category"]).any():
        raise ValueError("FIES contains duplicate keys")
    expected_keys = {(geography, decile, category)
                     for geography in GEOGRAPHY_LABELS.values()
                     for decile in range(11)
                     for category in CATEGORY_LABELS.values()}
    actual_keys = set(frame[["geography", "income_decile", "category"]].itertuples(index=False, name=None))
    if actual_keys != expected_keys:
        raise ValueError("FIES selected geography, decile, or category coverage is incomplete")
    amounts = frame.loc[frame["category"] == "total_expenditure_million_php"]
    shares = frame.loc[frame["category"] != "total_expenditure_million_php"]
    if (amounts["value"] <= 0).any() or not amounts["unit"].eq("million_php").all():
        raise ValueError("FIES total expenditure amount or unit is invalid")
    if not shares["value"].between(0, 100).all() or not shares["unit"].eq("percent_of_group_expenditure").all():
        raise ValueError("FIES expenditure share or unit is invalid")
    checks = []
    for geography in GEOGRAPHY_LABELS.values():
        regional_amounts = amounts.loc[amounts["geography"] == geography]
        total = float(regional_amounts.loc[regional_amounts["income_decile"] == 0, "value"].iloc[0])
        decile_total = float(regional_amounts.loc[regional_amounts["income_decile"] > 0, "value"].sum())
        if abs(total - decile_total) > 0.1:
            raise ValueError("FIES decile expenditures do not reconcile to all-income total")
        for category in CATEGORY_LABELS.values():
            if category == "total_expenditure_million_php":
                continue
            category_shares = shares.loc[(shares["geography"] == geography) & (shares["category"] == category)]
            decile_shares = category_shares.loc[category_shares["income_decile"] > 0, ["income_decile", "value"]]
            weighted = decile_shares.merge(regional_amounts[["income_decile", "value"]],
                                           on="income_decile", validate="one_to_one", suffixes=("_share", "_amount"))
            reconstructed = float((weighted["value_share"] * weighted["value_amount"]).sum() /
                                  weighted["value_amount"].sum())
            published = float(category_shares.loc[category_shares["income_decile"] == 0, "value"].iloc[0])
            checks.append(abs(reconstructed - published))
    maximum_deviation = max(checks)
    if maximum_deviation > tolerance_percentage_points:
        raise ValueError("FIES decile-weighted shares do not reconcile to all-income shares")
    return {"rows": len(frame), "geographies": 2, "income_groups_per_geography": 11,
            "categories_per_group": len(CATEGORY_LABELS), "missing_values": 0, "duplicate_keys": 0,
            "share_minimum_percent": float(shares["value"].min()),
            "share_maximum_percent": float(shares["value"].max()),
            "maximum_weighted_share_deviation_percentage_points": maximum_deviation,
            "weighted_share_tolerance_percentage_points": tolerance_percentage_points}


def summarize_fies(frame: pd.DataFrame) -> pd.DataFrame:
    wide = frame.pivot(index=["geography", "income_decile"], columns="category", values="value").reset_index()
    wide.columns.name = None
    wide["selected_essential_share_percent"] = wide[list(ESSENTIAL_CATEGORIES)].sum(axis=1)
    return wide.sort_values(["geography", "income_decile"]).reset_index(drop=True)
