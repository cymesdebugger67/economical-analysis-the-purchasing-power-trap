import calendar
import json
from pathlib import Path

import pandas as pd


GEOGRAPHIES = {"PHILIPPINES", "..Region XI (Davao Region)"}
COMMODITIES = {
    "0 - ALL ITEMS": "all_items",
    "01 - FOOD AND NON-ALCOHOLIC BEVERAGES": "food_and_beverages",
    "04 - HOUSING, WATER, ELECTRICITY, GAS, AND OTHER FUELS": "housing_and_utilities",
    "07 - TRANSPORT": "transport",
}
MONTHS = {month: index for index, month in enumerate(calendar.month_abbr) if month}


def load_pxweb_records(path: Path) -> pd.DataFrame:
    source = json.loads(path.read_text(encoding="utf-8"))
    variables = source["metadata"]["variables"]
    code_labels = {variable["code"]: dict(zip(variable["values"], variable["valueTexts"]))
                   for variable in variables}
    dimensions = [column["code"] for column in source["observations"]["columns"] if column["type"] != "c"]
    records = []
    for item in source["observations"]["data"]:
        if len(item["key"]) != len(dimensions) or len(item["values"]) != 1:
            raise ValueError("Unexpected PSA observation shape")
        record = {name: code_labels[name][value] for name, value in zip(dimensions, item["key"])}
        record["value"] = item["values"][0]
        records.append(record)
    return pd.DataFrame.from_records(records)


def prepare_monthly_series(records: pd.DataFrame, is_cpi: bool) -> pd.DataFrame:
    frame = records.copy()
    if set(frame["Geolocation"]) != GEOGRAPHIES:
        raise ValueError("Unexpected geography in PSA extract")
    if is_cpi and set(frame["Commodity Description"]) != set(COMMODITIES):
        raise ValueError("Unexpected commodity hierarchy in PSA extract")
    if not is_cpi and set(frame["Description"]) != {"Purchasing Power of Peso"}:
        raise ValueError("Unexpected PSA purchasing-power definition")
    if set(frame["Period"]) - set(MONTHS):
        raise ValueError("Non-monthly period in PSA extract")
    frame["month"] = pd.to_datetime(frame["Year"].astype(str) + "-" +
                                    frame["Period"].map(MONTHS).astype(str) + "-01")
    frame["value"] = pd.to_numeric(frame["value"], errors="raise")
    frame["geography"] = frame["Geolocation"].map({"PHILIPPINES": "philippines",
                                                      "..Region XI (Davao Region)": "davao_region"})
    if is_cpi:
        frame["commodity"] = frame["Commodity Description"].map(COMMODITIES)
        return frame[["month", "geography", "commodity", "value"]].rename(columns={"value": "cpi"})
    return frame[["month", "geography", "value"]].rename(columns={"value": "official_ppp"})


def load_wage_events(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["effective_date"])
    required = {"effective_date", "wage_order", "daily_wage_php", "source_page"}
    if set(frame) != required:
        raise ValueError("Unexpected wage event schema")
    frame["daily_wage_php"] = pd.to_numeric(frame["daily_wage_php"], errors="raise")
    return frame.sort_values("effective_date").reset_index(drop=True)
