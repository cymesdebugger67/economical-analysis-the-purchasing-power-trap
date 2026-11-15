# Methodology

## Research contract

The question is whether changes in the Region XI statutory non-agricultural daily minimum wage kept pace with consumer prices from January 2018 through December 2025. The descriptive propositions are that the nominal wage may rise faster, slower, or at the same pace as regional prices, and that the answer may change with the deflator or the handling of mid-month wage orders. The Philippines is a CPI benchmark, not a national wage comparison.

The measured population is **a statutory rate**, not earnings received by a representative worker. This study cannot estimate compliance, hours worked, employment, take-home pay, family income, poverty, or welfare. It makes no causal claim about wages and inflation.

## Series and units

PSA OpenSTAT table `0012M4ACP22.px` supplies monthly all-income-household CPI, 2018 annual average = 100, using the `2018NEW` geographic classification. The extract retains exactly `PHILIPPINES` and `Region XI (Davao Region)`, and the top-level all-items, food and non-alcoholic beverages, housing and utilities, and transport groups. Their CPI values are separate indices and are never added together. Month labels `Jan` through `Dec` are accepted; `Ave` is excluded. The intended window contains 96 months for each series. The 2018 base is the annual average, so January 2018 need not equal 100.

PSA table `0012M4ACP24.px` supplies the official purchasing power of one peso, rounded to two decimals. It is used to reconcile `100/CPI`, not as a separate deflator. The NWPC Region XI non-agricultural schedule provides eight effective-dated rates from May 2017 to March 2025. The baseline rate is included to cover January 2018. Rates are PHP per day, before deductions. The schedule's non-agricultural coverage and any legal exemptions must not be confused with an observed population-wide wage.

## Calculations

For month `t` and a chosen CPI group:

- Monthly CPI change: `(CPI_t / CPI_(t-1) - 1) × 100`.
- Year-over-year CPI change: `(CPI_t / CPI_(t-12) - 1) × 100`.
- Cumulative CPI change from January 2018: `(CPI_t / CPI_2018-01 - 1) × 100`.
- Purchasing power of one peso against the 2018 base: `100 / CPI_t`.
- Real statutory daily wage in 2018 pesos: `nominal daily wage × 100 / CPI_t`.
- Indexed wage and CPI: each divided by its own January 2018 value, then multiplied by 100.
- Real wage change from January 2018: `(real wage_t / real wage_2018-01 - 1) × 100`.

The main monthly wage measure is the rate in force on the **last calendar day** of the month. A robustness measure averages the statutory rate applicable on each calendar day of the month. This is a timing sensitivity, not an estimate of paid working days or actual earnings. Wage effective dates are inclusive. The alternative food CPI deflator tests whether a food-focused price measure changes the descriptive result; it is not a personalized cost-of-living index.

## Validation and interpretation

The pipeline rejects missing, duplicate, nonpositive, out-of-range or mismatched observations; checks all expected month keys; requires a wage rate before the study starts; validates CPI-to-wage joins; checks 2018 averages near 100 within rounding; and reconciles the official PPP series to `100/CPI` within 0.006 peso. It checks stored raw-file SHA-256 digests before analysis. No official observation is interpolated. Automated tests use invented values only as test fixtures.

The analysis is descriptive. CPI is a representative index, not a household expenditure record. Food, housing, and transport CPIs are broad categories; category inflation need not match any household's basket. The FIES 2023 preliminary expenditure-share workbook was identified but could not be downloaded during this batch because the PSA attachment returned HTTP 403. No FIES figures, weights, or affordability scenario enter the current calculations. A future FIES extract should be labeled by vintage and used only as cross-sectional context, never monthly household spending.

The new geographic-code CPI series is used consistently for both geographies throughout the window. The analysis does not splice in the old-code table. Published CPI and PPP are rounded; real wage estimates inherit that rounding. A later re-run may produce revised observations if PSA updates the table, so the raw manifest and its hashes identify this run.
