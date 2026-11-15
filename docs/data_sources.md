# Data sources and provenance

Accessed 16 November 2026 (Asia/Manila). Raw downloads and API replies are stored locally in `data/raw/` and excluded from Git. The public figures and summary tables are derived outputs. Re-run with `python scripts/run_analysis.py --acquire` to refresh official sources; compare the new manifest before treating revised values as the same vintage.

| Source | Authority and exact URL | Extraction and coverage | Local SHA-256 |
| --- | --- | --- | --- |
| CPI, `0012M4ACP22.px` | [PSA OpenSTAT API](https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/0012M4ACP22.px) | API metadata GET, then narrow JSON POST; 2 geographies × 4 top-level categories × 8 years × 12 months = 768 values. `Ave` omitted. January 2018–December 2025, 2018=100. | `f7614ce465007af54294e988a938f89fc9556ee986f413416a9c57477096880c` |
| Purchasing power of peso, `0012M4ACP24.px` | [PSA OpenSTAT API](https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/0012M4ACP24.px) | Same API mechanism; 2 geographies × 96 months = 192 values. | `23beef70e1ef665428a9e431863b25da13753daf49ff4d77baf9438c97cf3e96` |
| Historical non-agricultural daily wage rates, schedule dated 6 November 2026 | [NWPC historical schedule PDF](https://nwpc.dole.gov.ph/wp-content/uploads/2026/11/2-Summary-of-DMWR-per-Wage-Order-by-Region_Non-Agriculture-1989-to-Nov_6_2026.pdf) and [NWPC Region XI order index](https://nwpc.dole.gov.ph/region-xi/) | PDF GET. Region XI schedule, PDF page 9, manually transcribed into `data/reference/region_xi_wage_events.csv`: 8 rate events from 1 May 2017 through 7 March 2025. The order index provides original-order links for follow-up review. | `e29f152c0f7cc6cd741a41a9ac718b44e1f7ec6e741162bbee45f6419e7cd7ac` |

The PSA catalog described the CPI and PPP tables as extending through October 2026 and listed an update time of 5 November 2026. The query deliberately stops at December 2025. The raw JSON includes the exact query and metadata; the raw manifest records retrieval date and hashes. The old-geographic-code CPI table was not used.

NWPC schedule rates used (PHP/day): 340 from 1 May 2017 (XI-19); 370 from 16 August 2018 and 396 from 16 February 2019 (XI-20); 427 from 19 June 2022 and 443 from 1 January 2023 (XI-21); 462 from 6 March 2024 and 481 from 1 September 2024 (XI-22); 510 from 7 March 2025 (XI-23). These are the schedule's non-agricultural rates, not observed pay. Original wage orders and their implementing rules should be reviewed for any exemption or sector nuance before the final release.

## Secondary context pending

The [PSA 2023 FIES release](https://psa.gov.ph/statistics/income-expenditure/fies/node/1684064928) links its “Table 7. 2018, 2021 and 2023p Share to Total Family Expenditure, by Region, Province and HUC” workbook at [this official attachment](https://psa.gov.ph/system/files/iesd/Table%207.%202018%2C%202021%20and%202023p%20Share%20to%20Total%20Family%20Expenditure%2C%20by%20Region%2C%20Province%20and%20HUC.xlsx). Direct attachment retrieval returned HTTP 403 on 16 November 2026, so no FIES statistics were incorporated. The `2023p` label indicates preliminary values in that publication. The [PSA FIES landing page](https://psa.gov.ph/statistics/income-expenditure/fies) also hosts preliminary 2025 outputs; they are not mixed into this analysis.

PSA's site states [CC BY 4.0 unless otherwise noted](https://psa.gov.ph/statistics/income-expenditure/fies). NWPC's site states government content is public domain unless otherwise stated; verify file-specific terms before redistributing source PDFs or workbooks. This repository attributes PSA and NWPC and does not commit raw source files.
