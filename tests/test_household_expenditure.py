import unittest

import pandas as pd

from purchasing_power.household_expenditure import CATEGORY_LABELS, GEOGRAPHY_LABELS, prepare_fies, summarize_fies, validate_fies


def synthetic_fies() -> pd.DataFrame:
    records = []
    for geography in GEOGRAPHY_LABELS.values():
        for income_decile in range(11):
            for category in CATEGORY_LABELS.values():
                is_amount = category == "total_expenditure_million_php"
                records.append({"geography": geography, "income_decile": income_decile,
                                "category": category, "value": 100.0 if is_amount and income_decile == 0
                                else 10.0, "unit": "million_php" if is_amount
                                else "percent_of_group_expenditure"})
    return pd.DataFrame.from_records(records)


class HouseholdExpenditureTest(unittest.TestCase):
    def test_valid_fixture_keeps_amounts_separate_from_shares(self):
        frame = synthetic_fies()
        diagnostics = validate_fies(frame)
        self.assertEqual(diagnostics["rows"], 176)
        summary = summarize_fies(frame)
        self.assertEqual(summary.loc[0, "total_expenditure_million_php"], 100)
        self.assertEqual(summary.loc[0, "selected_essential_share_percent"], 30)

    def test_share_above_100_fails(self):
        frame = synthetic_fies()
        frame.loc[frame.category.eq("food_and_beverages").idxmax(), "value"] = 101
        with self.assertRaisesRegex(ValueError, "share"):
            validate_fies(frame)

    def test_amount_unit_cannot_be_percentage(self):
        frame = synthetic_fies()
        frame.loc[frame.category.eq("total_expenditure_million_php"), "unit"] = "percent_of_group_expenditure"
        with self.assertRaisesRegex(ValueError, "amount or unit"):
            validate_fies(frame)

    def test_duplicate_and_missing_decile_fail(self):
        frame = synthetic_fies()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_fies(pd.concat([frame, frame.iloc[[0]]], ignore_index=True))
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate_fies(frame.iloc[1:].reset_index(drop=True))

    def test_decile_weighted_share_mismatch_fails(self):
        frame = synthetic_fies()
        frame.loc[(frame.geography.eq("davao_region")) & (frame.income_decile.eq(0)) &
                  (frame.category.eq("food_and_beverages")), "value"] = 20
        with self.assertRaisesRegex(ValueError, "reconcile"):
            validate_fies(frame)

    def test_parent_child_category_is_rejected(self):
        frame = pd.DataFrame({"Region, Province, and HUC": ["REGION XI - DAVAO REGION", "PHILIPPINES"],
                              "Major Expenditure Group": ["..Food Consumed at Home"] * 2,
                              "Indicator": ["1st Decile"] * 2, "value": [10] * 2})
        with self.assertRaisesRegex(ValueError, "hierarchy"):
            prepare_fies(frame)


if __name__ == "__main__":
    unittest.main()
