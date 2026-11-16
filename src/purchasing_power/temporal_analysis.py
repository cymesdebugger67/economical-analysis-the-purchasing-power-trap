import pandas as pd


def below_reference_episodes(wages: pd.DataFrame) -> pd.DataFrame:
    frame = wages.loc[wages["commodity"] == "all_items"].sort_values("month").reset_index(drop=True)
    below = frame["real_wage_change_percent"] < 0
    episode_number = below.ne(below.shift(fill_value=False)).cumsum()
    records = []
    for _, group in frame.loc[below].groupby(episode_number[below]):
        trough = group.loc[group["real_wage_change_percent"].idxmin()]
        records.append({"start_month": group["month"].iloc[0], "end_month": group["month"].iloc[-1],
                        "months": len(group), "trough_month": trough["month"],
                        "trough_change_percent": float(trough["real_wage_change_percent"])})
    return pd.DataFrame.from_records(records, columns=["start_month", "end_month", "months", "trough_month",
                                                     "trough_change_percent"])


def peak_to_trough_drawdown(wages: pd.DataFrame) -> dict:
    frame = wages.loc[wages["commodity"] == "all_items"].sort_values("month").reset_index(drop=True)
    peaks = frame["real_wage_2018_php"].cummax()
    drawdown = (frame["real_wage_2018_php"] / peaks - 1) * 100
    trough_index = int(drawdown.idxmin())
    peak_index = int(frame.loc[:trough_index, "real_wage_2018_php"].idxmax())
    return {"peak_month": frame.loc[peak_index, "month"].strftime("%Y-%m"),
            "peak_real_wage_2018_php": float(frame.loc[peak_index, "real_wage_2018_php"]),
            "trough_month": frame.loc[trough_index, "month"].strftime("%Y-%m"),
            "trough_real_wage_2018_php": float(frame.loc[trough_index, "real_wage_2018_php"]),
            "drawdown_percent": float(drawdown.iloc[trough_index])}


def wage_event_windows(wages: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    all_items = wages.loc[wages["commodity"] == "all_items"].set_index("month")
    records = []
    for event in events.itertuples(index=False):
        month = event.effective_date.to_period("M").to_timestamp()
        if month not in all_items.index or month - pd.offsets.MonthBegin(1) not in all_items.index:
            continue
        prior = all_items.loc[month - pd.offsets.MonthBegin(1)]
        current = all_items.loc[month]
        records.append({"wage_order": event.wage_order, "effective_date": event.effective_date,
                        "prior_month": prior.name, "event_month": month,
                        "prior_wage_php": float(prior["nominal_wage_php"]),
                        "new_wage_php": float(current["nominal_wage_php"]),
                        "nominal_increase_php": float(current["nominal_wage_php"] - prior["nominal_wage_php"]),
                        "prior_cpi": float(prior["cpi"]), "event_month_cpi": float(current["cpi"]),
                        "real_wage_change_percent": float((current["real_wage_2018_php"] /
                                                           prior["real_wage_2018_php"] - 1) * 100)})
    return pd.DataFrame.from_records(records)


def endpoint_decomposition(wages: pd.DataFrame, cpi: pd.DataFrame) -> dict:
    all_items = wages.loc[wages["commodity"] == "all_items"].sort_values("month")
    first, last = all_items.iloc[0], all_items.iloc[-1]
    nominal_ratio = float(last["nominal_wage_php"] / first["nominal_wage_php"])
    price_ratio = float(last["cpi"] / first["cpi"])
    national = cpi.loc[(cpi["commodity"] == "all_items") &
                       (cpi["geography"] == "philippines")].sort_values("month")
    national_price_ratio = float(national["cpi"].iloc[-1] / national["cpi"].iloc[0])
    return {"reference_month": first["month"].strftime("%Y-%m"),
            "end_month": last["month"].strftime("%Y-%m"),
            "nominal_wage_ratio": nominal_ratio, "regional_price_ratio": price_ratio,
            "real_wage_ratio": nominal_ratio / price_ratio,
            "national_price_ratio": national_price_ratio,
            "regional_minus_national_cumulative_price_change_percentage_points":
                (price_ratio - national_price_ratio) * 100}
