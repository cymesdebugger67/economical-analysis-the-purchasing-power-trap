# Analytical methodology

## Research design

This descriptive study evaluates whether the **selected statutory minimum-wage benchmark** kept pace with regional consumer prices in Davao Region during January 2018–December 2025. It deliberately separates three questions: (1) endpoint purchasing-power change, (2) erosion and recovery *between* endpoints, and (3) how 2023 household expenditure shares differ by per-capita-income decile. It cannot infer causal effects of wage regulations or actual household welfare.

## Source measures and units

The PSA 2018-base CPI measures the price of a representative consumption basket and is expressed with **calendar-year 2018 annual average=100**. Two geographies are used throughout: Davao Region and the Philippines, using the same PSA `2018NEW` geography coding. Four independently indexed groups are selected: all items; food and non-alcoholic beverages; housing, water, electricity, gas and other fuels; transport. They are not added together. Monthly Jan–Dec values exclude `Ave` rows. The 96 months per series run January 2018 through December 2025.

The purchasing-power-of-the-peso table supplies rounded official values for independent reconciliation, not for a second index. The wage-event table represents the **non-agricultural larger-establishment benchmark** for the full interval, checked against NWPC original wage orders XI-19 through XI-23. It is **not a universally applicable wage** for every non-agricultural employee before the April 2023 category consolidation. The source of the 2016 baseline rate and the May 2017 COLA integration are explained in [the legal-rate audit](wage_order_audit.md). Subsequent 2026 wage increases are excluded by study design.

## Calculation rules

For geography and CPI commodity series \(j\):

- Monthly CPI change is \((CPI_{j,t}/CPI_{j,t-1}-1)\times100\).
- Year-over-year CPI change is \((CPI_{j,t}/CPI_{j,t-12}-1)\times100\).
- Cumulative price change from January 2018 is \((CPI_{j,t}/CPI_{j,2018\text{-}01}-1)\times100\).
- Purchasing power per nominal peso in 2018 pesos is \(100/CPI_{j,t}\).
- Real statutory daily wage in 2018 pesos is \(W_t\times100/CPI_{j,t}\).
- January-2018-indexed wage and CPI are each divided by **their own** January 2018 values and multiplied by 100.
- Real-wage percentage change from January 2018 is \((W_t^{real}/W_{2018\text{-}01}^{real}-1)\times100\).

A **month-end** statutory daily wage is assigned to each month from its latest effective order. This is a point-in-time legal-rate convention. A **calendar-day-weighted** alternative averages the prevailing statutory benchmark across calendar days of each month; effective dates are inclusive. Neither series represents paid workdays or wages received. An alternative food CPI is a **single-category deflator**, not a decile-specific household basket or a measured cost of living.

Below-reference episodes are consecutive months when the all-items-deflated statutory wage falls below the January 2018 real-wage level. A peak-to-trough drawdown instead measures the largest decline from an **earlier observed monthly peak** in this 96-month real-wage trajectory. The two metrics have different comparison reference points. Wage-event windows compare the preceding month to the effective month; their change is descriptive, not attributable to the regulation as a causal effect.

For endpoints 0 and T, the exact multiplicative identity is:

\[
\frac{W_T^{real}}{W_0^{real}}=\frac{W_T^{nominal}/W_0^{nominal}}{CPI_T/CPI_0}.
\]

The regional-national cumulative CPI difference is a *difference in percentage points of endpoint changes*, not a growth-rate differential for all intervening months.

## FIES expenditure composition

The 2023 PSA FIES OpenSTAT Table 7 reports total annual family expenditure **in millions of pesos** and major expenditure-group **shares of total annual family expenditure within the same geography and per-capita-income decile**. The household/family is the survey unit; deciles rank families by *per-capita family income*. The aggregate `All Income Groups` entry is not an eleventh income decile. The selected extract has two geographies, ten deciles plus an aggregate group, and seven selected major expenditure shares plus one total-expenditure amount per group, for **176 values**.

Group labels are top-level categories; subcategories with nested prefixes are excluded to avoid double counting. Food, housing/utilities, and transport are added only as **percentages of the same decile's total expenditure**. The seven selected expenditure groups do not exhaust the full household spending classification, so their sum is not required to equal 100%. Published decile-specific percentages are reconciled to the all-income-groups percentage using published decile expenditure totals as weights, with a 0.15-percentage-point tolerance for rounding.

The FIES snapshot is **2023 cross-sectional context**. It is neither a monthly time series nor a mapping from statutory minimum-wage earners to FIES income deciles. No family-specific CPI, personalized inflation index, or monthly household affordability claim is constructed. The FIES table uses the 2020 PCOICOP group structure and is not automatically compatible with the 2018-base CPI group classification for creating a weighted inflation index.

## Data quality and reproducibility

- **Completeness:** fixed 96-month coverage for every CPI and PPP series, 176 cross-sectional FIES entries, full statutory-rate coverage.
- **Accuracy:** official `100/CPI` reconciliation within 0.006 peso after rounding; base-year CPI arithmetic; audited wage order documents; published aggregate FIES checks.
- **Consistency:** geography keys, category labels, data types, CPI base period, original order IDs and effective dates, FIES amounts versus percentages.
- **Integrity:** unique composite keys, validated join multiplicity, source and frozen-input SHA-256 hashes; explicit failures on tampering or missing data.
- **Validation:** automated edge cases for effective dates and leap years, malformed CPI and FIES observations, real-wage arithmetic and the frozen replay contract.

No missing official observation is interpolated. Source extraction happens via documented narrow PSA PxWeb API queries. The source vintage is preserved as hashes of raw responses; an additional small, selected-observation **frozen snapshot** enables offline reproduction. A fresh API pull can be revised independently of the captured snapshot, so it is written to a separate timestamped vintage. See [sources](data_sources.md) for the exact authority and attribution.

## Interpretation limits

The wage benchmark is not actual pay, total take-home income, hours worked, compliance, household income or employment status. Its pre-April-2023 applicability differs from some smaller retail/service workplaces. CPI does not represent every household's purchases; food-only deflation is not an individual exposure estimate. FIES composition documents group-level family expenditure shares, not individual workers' realized inflation. Statistical significance tests and forecast models are not used because the central questions are transparent descriptive comparisons of administrative and aggregate statistical series, not a sampling-based causal estimand.
