import unittest
import json
import tempfile
from pathlib import Path

import pandas as pd

from purchasing_power.analysis import calculate_cpi_metrics, calculate_wage_metrics, monthly_wage_rates
from purchasing_power.preparation import load_pxweb_records
from purchasing_power.sources import WAGE_ORDER_URLS
from purchasing_power.validation import validate_base_year, validate_monthly_series, validate_ppp_reconciliation, validate_wage_event_audit, validate_wage_events


class EconomicCalculationsTest(unittest.TestCase):
    def test_cpi_changes_and_purchasing_power(self):
        months = pd.date_range("2018-01-01", periods=13, freq="MS")
        cpi = pd.DataFrame({"month": months, "geography": "davao_region",
                            "commodity": "all_items", "cpi": [100.0] * 12 + [110.0]})
        result = calculate_cpi_metrics(cpi)
        self.assertAlmostEqual(result.iloc[-1]["monthly_change_percent"], 10.0)
        self.assertAlmostEqual(result.iloc[-1]["year_over_year_percent"], 10.0)
        self.assertAlmostEqual(result.iloc[-1]["cumulative_change_percent"], 10.0)
        self.assertAlmostEqual(result.iloc[-1]["purchasing_power_per_peso"], 100 / 110)
        self.assertTrue(pd.isna(result.iloc[0]["year_over_year_percent"]))

    def test_mid_month_wage_assignment(self):
        events = pd.DataFrame({"effective_date": pd.to_datetime(["2017-05-01", "2018-08-16"]),
                               "daily_wage_php": [340, 370]})
        result = monthly_wage_rates(events, pd.DatetimeIndex(["2018-07-01", "2018-08-01"]))
        self.assertEqual(result.iloc[0]["nominal_wage_php"], 340)
        self.assertEqual(result.iloc[1]["nominal_wage_php"], 370)
        self.assertAlmostEqual(result.iloc[1]["day_weighted_wage_php"], (15 * 340 + 16 * 370) / 31)

    def test_missing_baseline_wage_fails(self):
        events = pd.DataFrame({"effective_date": pd.to_datetime(["2018-02-01"]), "daily_wage_php": [340]})
        with self.assertRaises(ValueError):
            monthly_wage_rates(events, pd.DatetimeIndex(["2018-01-01"]))

    def test_real_wage_and_reference_index(self):
        cpi = pd.DataFrame({"month": pd.to_datetime(["2018-01-01", "2018-02-01"]),
                            "geography": "davao_region", "commodity": "all_items", "cpi": [100, 125]})
        wage = pd.DataFrame({"month": cpi["month"], "nominal_wage_php": [100, 120],
                             "day_weighted_wage_php": [100, 120]})
        result = calculate_wage_metrics(calculate_cpi_metrics(cpi), wage)
        self.assertAlmostEqual(result.iloc[1]["real_wage_2018_php"], 96)
        self.assertAlmostEqual(result.iloc[1]["real_wage_change_percent"], -4)
        self.assertAlmostEqual(result.iloc[1]["indexed_nominal_wage"], 120)
        self.assertAlmostEqual(result.iloc[1]["indexed_cpi"], 125)

    def test_missing_wage_join_fails(self):
        cpi = pd.DataFrame({"month": pd.to_datetime(["2018-01-01"]), "geography": "davao_region",
                            "commodity": "all_items", "cpi": [100]})
        wage = pd.DataFrame({"month": pd.to_datetime(["2018-02-01"]), "nominal_wage_php": [100],
                             "day_weighted_wage_php": [100]})
        with self.assertRaises(ValueError):
            calculate_wage_metrics(calculate_cpi_metrics(cpi), wage)

    def test_duplicate_cpi_key_fails(self):
        months = pd.date_range("2018-01-01", "2025-12-01", freq="MS")
        frame = pd.DataFrame({"month": list(months) + [months[0]], "geography": "davao_region",
                              "commodity": "all_items", "cpi": 100})
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_monthly_series(frame, ["geography", "commodity"], "cpi", 1)

    def test_missing_cpi_month_fails(self):
        months = pd.date_range("2018-01-01", "2025-11-01", freq="MS")
        frame = pd.DataFrame({"month": months, "geography": "davao_region",
                              "commodity": "all_items", "cpi": 100})
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate_monthly_series(frame, ["geography", "commodity"], "cpi", 1)

    def test_ppp_reconciliation_with_rounding(self):
        cpi = pd.DataFrame({"month": pd.to_datetime(["2018-01-01"]), "geography": "davao_region",
                            "commodity": "all_items", "cpi": [97.4]})
        ppp = pd.DataFrame({"month": pd.to_datetime(["2018-01-01"]), "geography": "davao_region",
                            "official_ppp": [1.03]})
        self.assertEqual(validate_ppp_reconciliation(cpi, ppp)["rows"], 1)
        ppp.loc[0, "official_ppp"] = 0.9
        with self.assertRaisesRegex(ValueError, "reconciliation"):
            validate_ppp_reconciliation(cpi, ppp)

    def test_base_year_check_rejects_wrong_scale(self):
        months = pd.date_range("2018-01-01", periods=12, freq="MS")
        frame = pd.DataFrame([{"month": month, "geography": geography, "commodity": commodity, "cpi": 100.0}
                              for geography in ("davao_region", "philippines")
                              for commodity in ("all_items", "food_and_beverages", "housing_and_utilities", "transport")
                              for month in months])
        self.assertEqual(validate_base_year(frame)["series"], 8)
        frame.loc[0, "cpi"] = 110
        with self.assertRaisesRegex(ValueError, "base-year"):
            validate_base_year(frame)

    def test_annual_base_does_not_require_january_to_equal_100(self):
        months = pd.date_range("2018-01-01", periods=12, freq="MS")
        values = [99] + [101] + [100] * 10
        frame = pd.DataFrame([{"month": month, "geography": geography, "commodity": commodity,
                               "cpi": value} for geography in ("davao_region", "philippines")
                              for commodity in ("all_items", "food_and_beverages", "housing_and_utilities", "transport")
                              for month, value in zip(months, values)])
        self.assertEqual(validate_base_year(frame)["maximum_absolute_deviation_from_100"], 0)

    def test_nonpositive_cpi_fails(self):
        months = pd.date_range("2018-01-01", "2025-12-01", freq="MS")
        frame = pd.DataFrame({"month": months, "geography": "davao_region",
                              "commodity": "all_items", "cpi": [0] + [100] * 95})
        with self.assertRaisesRegex(ValueError, "Nonpositive"):
            validate_monthly_series(frame, ["geography", "commodity"], "cpi", 1)

    def test_wage_event_audit_rejects_rate_mismatch(self):
        events = pd.DataFrame({"effective_date": pd.to_datetime(["2017-01-01", "2018-08-16"]),
                               "wage_order": ["XI-19", "XI-20"], "daily_wage_php": [100, 120]})
        audit = pd.DataFrame({"effective_date": events["effective_date"],
                              "wage_order": ["RB XI-19", "RB XI-20"],
                              "prior_rate_php": [90, 100], "new_rate_php": [100, 120],
                              "increase_php": [10, 20], "original_order_url":
                              [WAGE_ORDER_URLS["19"], WAGE_ORDER_URLS["20"]],
                              "order_page": [2, 2],
                              "verification_status": ["verified_original_order_and_nwpc_schedule"] * 2})
        self.assertEqual(validate_wage_event_audit(events, audit)["events_reconciled"], 2)
        audit.loc[1, "new_rate_php"] = 121
        with self.assertRaisesRegex(ValueError, "rates differ"):
            validate_wage_event_audit(events, audit)

    def test_duplicate_wage_date_fails(self):
        events = pd.DataFrame({"effective_date": pd.to_datetime(["2017-01-01", "2017-01-01"]),
                               "daily_wage_php": [100, 120]})
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_wage_events(events)

    def test_frozen_pxweb_record_decodes_deterministically(self):
        payload = {"metadata": {"variables": [{"code": "Geolocation", "values": ["0"],
                                               "valueTexts": ["PHILIPPINES"]}]},
                   "observations": {"columns": [{"code": "Geolocation", "type": "d"},
                                                {"code": "value", "type": "c"}],
                                    "data": [{"key": ["0"], "values": ["97.4"]}]}}
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "frozen_source.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            first = load_pxweb_records(path)
            second = load_pxweb_records(path)
            pd.testing.assert_frame_equal(first, second)
            self.assertEqual(first.iloc[0]["value"], "97.4")


if __name__ == "__main__":
    unittest.main()
