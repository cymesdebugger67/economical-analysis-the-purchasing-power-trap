import unittest

import pandas as pd

from purchasing_power.analysis import monthly_wage_rates
from purchasing_power.temporal_analysis import below_reference_episodes, endpoint_decomposition, peak_to_trough_drawdown, wage_event_windows


class TemporalAnalysisTest(unittest.TestCase):
    def test_leap_february_and_last_day_effectivity(self):
        events = pd.DataFrame({"effective_date": pd.to_datetime(["2020-01-01", "2020-02-16", "2020-02-29"]),
                               "daily_wage_php": [100, 200, 300]})
        result = monthly_wage_rates(events, pd.DatetimeIndex(["2020-02-01"]))
        self.assertEqual(result.iloc[0]["nominal_wage_php"], 300)
        self.assertAlmostEqual(result.iloc[0]["day_weighted_wage_php"], (15 * 100 + 13 * 200 + 300) / 29)

    def test_below_reference_episodes_and_drawdown(self):
        months = pd.date_range("2018-01-01", periods=6, freq="MS")
        values = [100, 95, 90, 110, 100, 105]
        frame = pd.DataFrame({"month": months, "commodity": "all_items",
                              "real_wage_2018_php": values,
                              "real_wage_change_percent": [value - 100 for value in values]})
        episodes = below_reference_episodes(frame)
        self.assertEqual(episodes["months"].tolist(), [2])
        self.assertEqual(episodes.iloc[0]["start_month"], months[1])
        drawdown = peak_to_trough_drawdown(frame)
        self.assertEqual(drawdown["peak_month"], "2018-01")
        self.assertEqual(drawdown["trough_month"], "2018-03")
        self.assertAlmostEqual(drawdown["drawdown_percent"], -10)

    def test_endpoint_ratios_are_multiplicative(self):
        months = pd.to_datetime(["2018-01-01", "2025-12-01"])
        wages = pd.DataFrame({"month": months, "commodity": "all_items",
                              "nominal_wage_php": [100, 150], "cpi": [100, 125]})
        cpi = pd.DataFrame({"month": months, "commodity": "all_items", "geography": "philippines",
                            "cpi": [100, 120]})
        result = endpoint_decomposition(wages, cpi)
        self.assertAlmostEqual(result["real_wage_ratio"], 1.2)
        self.assertAlmostEqual(result["regional_minus_national_cumulative_price_change_percentage_points"], 5)

    def test_event_window_uses_prior_month_without_causal_claim(self):
        wages = pd.DataFrame({"month": pd.to_datetime(["2018-01-01", "2018-02-01"]),
                              "commodity": "all_items", "nominal_wage_php": [100, 120],
                              "cpi": [100, 110], "real_wage_2018_php": [100, 120 * 100 / 110]})
        events = pd.DataFrame({"effective_date": pd.to_datetime(["2018-02-16"]),
                               "wage_order": ["XI-20"], "daily_wage_php": [120]})
        result = wage_event_windows(wages, events)
        self.assertEqual(result.iloc[0]["nominal_increase_php"], 20)
        self.assertAlmostEqual(result.iloc[0]["real_wage_change_percent"], 9.09090909)


if __name__ == "__main__":
    unittest.main()
