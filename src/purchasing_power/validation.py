import pandas as pd

from purchasing_power.sources import WAGE_ORDER_URLS


START_MONTH = pd.Timestamp("2018-01-01")
END_MONTH = pd.Timestamp("2025-12-01")
EXPECTED_MONTHS = pd.date_range(START_MONTH, END_MONTH, freq="MS")


def validate_monthly_series(frame: pd.DataFrame, group_columns: list[str], value_column: str,
                            expected_groups: int) -> dict:
    if frame.empty or frame[group_columns + ["month", value_column]].isna().any().any():
        raise ValueError(f"Missing {value_column} data")
    if (frame[value_column] <= 0).any():
        raise ValueError(f"Nonpositive {value_column} value")
    if frame.duplicated(group_columns + ["month"]).any():
        raise ValueError(f"Duplicate {value_column} observation")
    groups = list(frame.groupby(group_columns[0] if len(group_columns) == 1 else group_columns, dropna=False))
    if len(groups) != expected_groups:
        raise ValueError(f"Expected {expected_groups} {value_column} groups, found {len(groups)}")
    for key, group in groups:
        if set(group["month"]) != set(EXPECTED_MONTHS):
            missing = sorted(set(EXPECTED_MONTHS) - set(group["month"]))
            extra = sorted(set(group["month"]) - set(EXPECTED_MONTHS))
            raise ValueError(f"Invalid coverage for {key}: missing={missing}, extra={extra}")
    return {"rows": len(frame), "groups": len(groups), "months_per_group": len(EXPECTED_MONTHS),
            "missing_values": 0, "duplicate_keys": 0, "minimum": float(frame[value_column].min()),
            "maximum": float(frame[value_column].max())}


def validate_wage_events(events: pd.DataFrame) -> dict:
    if events.empty or events.isna().any().any():
        raise ValueError("Missing wage event data")
    if events["effective_date"].duplicated().any():
        raise ValueError("Duplicate wage effective date")
    if not events["effective_date"].is_monotonic_increasing:
        raise ValueError("Wage events are not ordered")
    if events["effective_date"].iloc[0] > START_MONTH:
        raise ValueError("No wage rate covers the first month")
    if (events["daily_wage_php"] <= 0).any():
        raise ValueError("Nonpositive statutory wage")
    if events["effective_date"].iloc[-1] > END_MONTH + pd.offsets.MonthEnd(0):
        raise ValueError("Wage event occurs after study period")
    return {"events": len(events), "baseline_date": str(events["effective_date"].iloc[0].date()),
            "last_effective_date": str(events["effective_date"].iloc[-1].date()),
            "minimum_wage_php": float(events["daily_wage_php"].min()),
            "maximum_wage_php": float(events["daily_wage_php"].max())}


def validate_wage_event_audit(events: pd.DataFrame, audit: pd.DataFrame) -> dict:
    required = {"effective_date", "wage_order", "prior_rate_php", "new_rate_php", "increase_php",
                "original_order_url", "order_page", "verification_status"}
    if set(audit) != required or len(audit) != len(events):
        raise ValueError("Wage audit schema or event count does not match")
    if audit.isna().any().any() or audit["effective_date"].duplicated().any():
        raise ValueError("Wage audit contains missing or duplicate events")
    merged = events.merge(audit, on="effective_date", how="outer", validate="one_to_one", indicator=True)
    if not merged["_merge"].eq("both").all():
        raise ValueError("Wage audit and event dates differ")
    if not (merged["wage_order_x"].str.replace("XI-", "") ==
            merged["wage_order_y"].str.replace("RB XI-", "")).all():
        raise ValueError("Wage audit order identifiers differ")
    if not (merged["daily_wage_php"] == merged["new_rate_php"]).all():
        raise ValueError("Wage audit rates differ")
    if not ((merged["new_rate_php"] - merged["prior_rate_php"]) == merged["increase_php"]).all():
        raise ValueError("Wage audit increases do not reconcile")
    if not (merged["prior_rate_php"].iloc[1:].reset_index(drop=True) ==
            merged["new_rate_php"].iloc[:-1].reset_index(drop=True)).all():
        raise ValueError("Wage audit rate sequence has a gap")
    if not all(row.original_order_url == WAGE_ORDER_URLS[row.wage_order_y.split("-")[-1]]
               for row in merged.itertuples(index=False)):
        raise ValueError("Wage audit source URL differs from official order index")
    if not merged["verification_status"].eq("verified_original_order_and_nwpc_schedule").all():
        raise ValueError("Wage audit contains an unverified event")
    return {"events_reconciled": len(merged), "rate_gaps": 0, "source_url_mismatches": 0}


def validate_base_year(cpi: pd.DataFrame, tolerance: float = 0.05) -> dict:
    averages = cpi.loc[cpi["month"].dt.year == 2018].groupby(["geography", "commodity"])["cpi"].mean()
    if len(averages) != 8:
        raise ValueError("Missing 2018 base-year series")
    maximum = float((averages - 100).abs().max())
    if maximum > tolerance:
        raise ValueError(f"2018 base-year average deviates by {maximum}")
    return {"series": len(averages), "maximum_absolute_deviation_from_100": maximum,
            "tolerance": tolerance}


def validate_ppp_reconciliation(cpi: pd.DataFrame, ppp: pd.DataFrame, tolerance: float = 0.006) -> dict:
    all_items = cpi.loc[cpi["commodity"] == "all_items", ["month", "geography", "cpi"]]
    merged = all_items.merge(ppp, on=["month", "geography"], how="outer", validate="one_to_one", indicator=True)
    if not merged["_merge"].eq("both").all():
        raise ValueError("CPI and official PPP month keys differ")
    deviation = (100 / merged["cpi"] - merged["official_ppp"]).abs()
    maximum = float(deviation.max())
    if maximum > tolerance:
        raise ValueError(f"Official PPP reconciliation failed: maximum difference {maximum}")
    return {"rows": len(merged), "maximum_absolute_deviation": maximum, "tolerance": tolerance}
