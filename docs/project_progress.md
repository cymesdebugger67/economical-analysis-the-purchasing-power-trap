# Project progress

**Owner and public author:** Cyril James Lunzaga

**Branch:** `feature/purchasing_power_analysis`

**Review date:** 16 November 2026 (Asia/Manila)
**Current phase:** 7, local checkpoint and owner review. Public release remains pending.

| Phase | Status | Acceptance evidence and remaining work |
| --- | --- | --- |
| 0. Repository initialization | Passed before this batch | Existing `main` baseline `7bb6588`, tracking `origin/main`, clean at intake. |
| 1. Scope and feasibility | Passed for core question | [Methodology](methodology.md) defines population, geography, 96-month window, measures and limits. PSA API and NWPC PDF were accessible. FIES is secondary and remains blocked. |
| 2. Source acquisition | Core passed; FIES partial | PSA CPI: 768 observations; PSA PPP: 192; NWPC schedule PDF downloaded. URLs, retrieval date and hashes in [data sources](data_sources.md). FIES 2023p Table 7 attachment returned HTTP 403. |
| 3. Preparation and QA | Passed for core extract | Eight CPI and two PPP series, 96 months each; zero missing values or duplicate keys; eight wage events cover January 2018 through December 2025. 2018-base averages and official PPP reconciliation pass. Diagnostics in `reports/tables/validation_diagnostics.json`. |
| 4. Economic analysis | Passed for statutory-rate measures | Monthly and annual CPI changes, January 2018 cumulative changes, PPP, effective wages, real wages, indexed comparisons, regional benchmark, commodity and timing sensitivities computed. No household scenario is claimed. |
| 5. Reporting | Initial figures passed | Five figures in `reports/figures/`; headline and commodity tables in `reports/tables/`; notebook reads processed outputs. Visual and interpretation review remains before public release. |
| 6. Testing and reproducibility | Initial checks passed | Nine offline `unittest` cases, 0 failures. Workspace virtual-environment editable install with existing system packages and offline pipeline run succeeded. Notebook's four code cells passed a non-interactive smoke check. Fresh dependency download in an empty environment remains unverified. |
| 7. Git release | Local checkpoint passed; public release pending | Core pipeline committed locally as `bb7d12d` on the feature branch. The presentation checkpoint and final Git status are reported with this batch. No push, merge, or publication authorized. |

## Core findings under review

The Davao all-items CPI was 97.4 in January 2018 and 131.4 in December 2025; the statutory non-agricultural rate was ₱340 and ₱510, respectively. Real statutory daily wages were ₱349.08 and ₱388.13 in 2018 pesos, an 11.19% endpoint gain relative to January 2018. Seven months fell below the January 2018 real-wage reference; the trough was July 2018 at -2.89%. This does not measure worker income or family welfare.

## Validation record

- CPI: 768 rows, 8 groups × 96 monthly dates; min 94.2, max 135.1; zero missing or duplicate keys.
- PSA PPP: 192 rows, 2 groups × 96 dates; min 0.76, max 1.03; zero missing or duplicate keys.
- PPP formula reconciliation: maximum absolute difference 0.004977 peso; tolerance 0.006 peso.
- Wage transcription: 8 ordered effective events; baseline 1 May 2017; latest 7 March 2025; PHP 340–510/day.
- 2018 base-year monthly means and raw SHA-256 checks are programmatically validated.
- Tests: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: 9 passed, 0 failed. `.\.venv\Scripts\python.exe scripts/run_analysis.py`: passed with the captured official extract. A global editable install failed because the sandbox could not write to the user site; the first workspace venv had old pip and setuptools, so tools were upgraded locally before its successful editable install.

## Local commit references

- `7bb6588` — pre-existing initial repository commit on `main`.
- `bb7d12d` — validated official-data pipeline, method, provenance, wage transcription, and tests on `feature/purchasing_power_analysis`.

## Issues and next actions

1. Obtain the 2023 FIES Region XI expenditure-share workbook via an official accessible route and document its preliminary vintage before adding context. No FIES values were guessed.
2. Review original Region XI wage orders for exemption and coverage nuances, especially before a final portfolio conclusion.
3. Review the chart and notebook presentation, then perform a clean reproduction from an isolated environment and final license/attribution check.
4. Seek explicit owner approval before pushing, merging, or publishing the branch.
