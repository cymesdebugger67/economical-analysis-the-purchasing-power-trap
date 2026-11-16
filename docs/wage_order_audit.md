# Region XI wage-order audit

The [machine-readable event audit](../data/reference/region_xi_wage_event_audit.csv) links each rate to an original NWPC order. The eight recorded rates and dates were checked against the [NWPC historical non-agricultural schedule](https://nwpc.dole.gov.ph/summary-of-daily-minimum-wage-rates-per-wage-order-by-region-non-agriculture-1989-present/) and the original order pages listed below. Raw PDF copies and their SHA-256 hashes are local and Git-ignored.

| Effective date | Order | Prior → new, PHP/day | Original verification |
| --- | --- | --- | --- |
| 16 Dec 2016 | [RB XI-19](https://nwpc.dole.gov.ph/wp-content/uploads/2023/04/reg-11-wo-19.pdf) | 317 → 340 | Page 2: non-agricultural industrial/commercial and retail/service with more than 10 workers. The 5-peso COLA was integrated into basic pay on 1 May 2017 without changing the total 340-peso rate. |
| 16 Aug 2018; 16 Feb 2019 | [RB XI-20](https://nwpc.dole.gov.ph/wp-content/uploads/2024/11/reg-11-wo-20.pdf) | 340 → 370 → 396 | Page 2: two tranches for the same larger-establishment benchmark. Smaller retail/service had a lower schedule. |
| 19 Jun 2022; 1 Jan 2023 | [RB XI-21](https://nwpc.dole.gov.ph/wp-content/uploads/2023/04/Published-WO-No.-RB-XI-21.pdf) | 396 → 427 → 443 | Page 2 gives the two benchmark tranches; page 3 records 19 June effectivity. Smaller retail/service reached 443 only on 1 April 2023. |
| 6 Mar 2024; 1 Sep 2024 | [RB XI-22](https://nwpc.dole.gov.ph/wp-content/uploads/2024/02/Wage-Order-No.-RB-XI-22.pdf) | 443 → 462 → 481 | Page 2 gives both rates and September date; page 3 records 6 March effectivity. |
| 7 Mar 2025 | [RB XI-23](https://nwpc.dole.gov.ph/wp-content/uploads/2025/02/Wage-Order-No.-RB-XI-23.pdf) | 481 → 510 | Page 2 gives the non-agricultural rate and 7 March effectivity. |

Before April 2023, the plotted rate represents the non-agricultural industrial/commercial and larger retail/service category. RB XI-21 phased smaller retail/service establishments into one non-agricultural rate by 1 April 2023. The plotted series therefore remains a consistent **larger-establishment benchmark** across the full study window; it must not be described as a rate that applied identically to every non-agricultural worker in every month.

The orders concern covered private-sector minimum wage earners and normal working hours of up to eight hours a day. RB XI-19 and RB XI-20 exclude domestic work and certain other categories in their coverage clauses and discuss calamity-related exemption applications and school-specific compliance timing. Those provisions affect legal applicability, not the arithmetic of this benchmark. This audit does not measure actual compliance, employment, or wages received.
