import calendar

import pandas as pd


def monthly_wage_rates(events: pd.DataFrame, months: pd.DatetimeIndex) -> pd.DataFrame:
    ordered = events.sort_values("effective_date").reset_index(drop=True)
    records = []
    for month in months:
        month_end = month + pd.offsets.MonthEnd(0)
        applicable = ordered.loc[ordered["effective_date"] <= month_end]
        if applicable.empty:
            raise ValueError(f"No wage rate for {month.date()}")
        month_end_wage = float(applicable["daily_wage_php"].iloc[-1])
        days = calendar.monthrange(month.year, month.month)[1]
        total = 0.0
        for day in range(1, days + 1):
            current = month + pd.Timedelta(days=day - 1)
            daily_applicable = ordered.loc[ordered["effective_date"] <= current]
            if daily_applicable.empty:
                raise ValueError(f"No wage rate for {current.date()}")
            total += float(daily_applicable["daily_wage_php"].iloc[-1])
        records.append({"month": month, "nominal_wage_php": month_end_wage,
                        "day_weighted_wage_php": total / days})
    return pd.DataFrame.from_records(records)


def calculate_cpi_metrics(cpi: pd.DataFrame) -> pd.DataFrame:
    frame = cpi.sort_values(["geography", "commodity", "month"]).copy()
    group = frame.groupby(["geography", "commodity"], sort=False)
    frame["monthly_change_percent"] = group["cpi"].pct_change() * 100
    frame["year_over_year_percent"] = group["cpi"].pct_change(12) * 100
    first = group["cpi"].transform("first")
    frame["cumulative_change_percent"] = (frame["cpi"] / first - 1) * 100
    frame["purchasing_power_per_peso"] = 100 / frame["cpi"]
    return frame


def calculate_wage_metrics(cpi_metrics: pd.DataFrame, wage_rates: pd.DataFrame) -> pd.DataFrame:
    regional = cpi_metrics.loc[cpi_metrics["geography"] == "davao_region"]
    frame = regional.merge(wage_rates, on="month", how="left", validate="many_to_one")
    if frame[["nominal_wage_php", "day_weighted_wage_php"]].isna().any().any():
        raise ValueError("CPI month lacks a wage rate")
    frame["real_wage_2018_php"] = frame["nominal_wage_php"] * 100 / frame["cpi"]
    frame["day_weighted_real_wage_2018_php"] = frame["day_weighted_wage_php"] * 100 / frame["cpi"]
    baseline = frame.loc[(frame["commodity"] == "all_items") &
                         (frame["month"] == pd.Timestamp("2018-01-01"))]
    if len(baseline) != 1:
        raise ValueError("Missing reference month")
    baseline_wage = float(baseline["nominal_wage_php"].iloc[0])
    frame["indexed_nominal_wage"] = frame["nominal_wage_php"] / baseline_wage * 100
    frame["indexed_cpi"] = frame["cpi"] / frame.groupby("commodity")["cpi"].transform("first") * 100
    frame["real_wage_change_percent"] = (frame["real_wage_2018_php"] /
                                         frame.groupby("commodity")["real_wage_2018_php"].transform("first") - 1) * 100
    return frame
