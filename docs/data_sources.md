# Official datasets, attribution and provenance

**Captured vintage:** 16 November 2026 (Asia/Manila) for the core CPI, PPP, NWPC history, and FIES extracts. Original responses and PDFs remain in the user's ignored `data/raw/` directory. The project includes a compact, checksum-verified, **transformed set of selected observations** in `data/frozen/` so documented results can be reproduced offline. No synthetic economic observations appear in the research data.

| Dataset | Official publisher and original resource | Selected coverage | Original captured SHA-256 |
| --- | --- | --- | --- |
| All-items and selected category CPI, 2018 base | [Philippine Statistics Authority, OpenSTAT `0012M4ACP22.px`](https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/0012M4ACP22.px) | Philippines + Davao Region; 4 top-level groups; 96 monthly periods; **768 values** | `f7614ce465007af54294e988a938f89fc9556ee986f413416a9c57477096880c` |
| Purchasing power of the peso | [PSA OpenSTAT `0012M4ACP24.px`](https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/0012M4ACP24.px) | Both geographies, 96 months; **192 values** | `23beef70e1ef665428a9e431863b25da13753daf49ff4d77baf9438c97cf3e96` |
| Historical non-agricultural minimum wage | [NWPC schedule as of 6 November 2026](https://nwpc.dole.gov.ph/wp-content/uploads/2026/11/2-Summary-of-DMWR-per-Wage-Order-by-Region_Non-Agriculture-1989-to-Nov_6_2026.pdf) and [Region XI order index](https://nwpc.dole.gov.ph/region-xi/) | Eight selected larger-establishment benchmark events from Dec 2016 through Mar 2025 | `e29f152c0f7cc6cd741a41a9ac718b44e1f7ec6e741162bbee45f6419e7cd7ac` |
| 2023 family expenditure by income decile | [PSA FIES OpenSTAT Table 7 `0071E3ATME0.px`](https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1E/IE/0071E3ATME0.px) and [table with definitions](https://openstat.psa.gov.ph/PXWeb/pxweb/en/DB/DB__1E__IE/0071E3ATME0.px) | Davao Region + Philippines; ten deciles plus aggregate; total expenditure + 7 top-level category shares; **176 values** | `dc64c218cc9369a270b79a151c9df837722ad5ca6810389462ae4b362bb502d7` |

The original PSA CPI query selected the `2018NEW` geographic classification (not the legacy series), years 2018–2025, months Jan–Dec (not the `Ave` aggregate), and four major groups. The official PPP is a rounded cross-check for the CPI calculation. The original JSON captures exact PxWeb metadata, selections and query values; `data/raw/source_manifest.json` records source file names and original digests.

The 2023 FIES direct spreadsheet attachment on a PSA release page originally returned HTTP 403. The alternative **official PSA OpenSTAT Table 7 API succeeded**. The saved `data/raw/psa_fies_2023_expenditure.json` includes the metadata, API POST query and selected observations; `data/raw/fies_manifest.json` records the extraction timestamp (`2026-11-15T22:28:23Z`, equivalent to 16 November Philippine time), original file hash and 176-cell response. The catalog showed an August 2026 update timestamp; the public FIES table's own displayed update date is January 23, 2026. These are metadata fields from different endpoints; the saved response and checksum determine the archived query vintage. The Table 7 footnote defines expenditure shares **within each per-capita-income decile**, not shares of a category allocated across deciles. The report retains exactly that definition.

## Original wage orders and rate categories

Source-linked event data are maintained in [`data/reference/region_xi_wage_events.csv`](../data/reference/region_xi_wage_events.csv) and the [`original order audit`](../data/reference/region_xi_wage_event_audit.csv). The corresponding NWPC original-order PDFs (XI-19, XI-20, XI-21, XI-22, XI-23) are downloaded only to ignored local raw storage. See [`wage_order_audit.md`](wage_order_audit.md) for the effective dates, COLA treatment, coverage distinctions and original links. **The plotted series is a selected non-agricultural larger-establishment benchmark, not a universally applicable historical rate.** The primary comparison ends in December 2025 and intentionally excludes the new 2026 wage order.

## Tracked frozen observation extracts

`data/frozen/manifest.json` records the checked-in normalized files, their SHA-256 hashes, the original source-file checksums and official URLs. They contain **only the narrow aggregate observations selected for this study**, not original full API tables, survey microdata or NWPC PDFs. The snapshot is suitable for a stable baseline, while live data may have changed since retrieval.

| Frozen file | Meaning | Rows |
| --- | --- | ---: |
| `data/frozen/monthly_cpi_2018_2025.csv` | Monthly CPI by geography and category | 768 |
| `data/frozen/monthly_purchasing_power_2018_2025.csv` | Official rounded purchasing-power values | 192 |
| `data/frozen/fies_expenditure_2023.csv` | FIES selected 2023 aggregate amounts and category shares | 176 |

To verify and replay: `python scripts/run_analysis.py --source frozen`. To process the original downloaded files: `python scripts/run_analysis.py --source captured`. To acquire a **new timestamped source vintage**, run `python scripts/run_analysis.py --refresh-vintage` with live network access and compare the new manifests before altering the baseline. Do not use `--acquire` on an existing `data/raw/source_manifest.json`, because this intentionally rejects overwriting a captured baseline. `python scripts/create_frozen_inputs.py --replace` is an explicit operation, intended only for a reviewed update of the frozen snapshot.

## Publisher credit and publication terms

**Philippine Statistics Authority (PSA)** is the originator of CPI, PPP and FIES aggregate statistics. The [PSA website states CC BY 4.0 unless otherwise noted](https://psa.gov.ph/nccrvs/memo-circulars); source links and transformations are acknowledged here and in figures. Verify any table-specific exceptions before public release. **National Wages and Productivity Commission (NWPC)** is the publisher of historical minimum-wage orders; rate extracts are attributed with original-order URLs. The repository does not include the original NWPC PDFs. Source-specific conditions must be respected. Public figures and tables are analytical derivatives, not official PSA or NWPC publications.
