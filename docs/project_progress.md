# Project execution and review record

**Project owner and sole public author:** Cyril James Lunzaga
**Review snapshot:** 16 November 2026 (Asia/Manila)
**Repository:** `economical-analysis-the-purchasing-power-trap`
**Development branch from uploaded archive:** `feature/purchasing_power_analysis`
**Last committed source baseline in archive:** `434f60a`
**Current stage:** Technical completion of the local source package; owner-controlled Git publication remains pending.

This record differentiates validated local code from GitHub publication. The uploaded archive included uncommitted work in progress. The continuation preserves those changes; replacing files from the handoff does **not** automatically create a commit, merge or push.

| Phase | Status | Completion evidence and remaining gate |
| --- | --- | --- |
| 0 — Local Git and remote | **Passed (previous work)** | Existing `main` baseline `7bb6588`, correct `origin`, development feature branch preserved. |
| 1 — Research contract | **Passed for defined scope** | [Methodology](methodology.md) specifies 2018–2025 Davao statutory benchmark, comparison definitions and exclusions. |
| 2 — Source acquisition | **Passed for captured vintage** | Official CPI 768, PPP 192, FIES 176; NWPC schedule and original orders XI-19–XI-23 present in uploaded ignored raw data; checksums verified in local runs. |
| 3 — Preparation and data QA | **Passed in local replay** | Full monthly coverage, no missing/duplicate monthly keys; FIES category, unit and weighted-share consistency checks pass; audit reconciles eight wage events. |
| 4 — Economic analysis | **Passed for selected metrics** | Endpoint real-wage gain +11.19%, seven below-reference months, maximum prior-peak drawdown −11.33%, category and timing sensitivities, FIES descriptive decile comparisons. |
| 5 — Figures and narrative | **Completed locally; owner visual signoff pending** | Eight individual output charts, one review contact sheet, project banner, notebook and revised portfolio README. |
| 6 — Reproducibility/testing | **Conditional** | 28/28 offline tests passed on Python 3.13.5; both captured and frozen pipeline paths completed with matching headline values; notebook code executed from root and notebook folder. A fresh isolated pip installation could not be completed because this container cannot reach the Python package index. A previously installed Python 3.9 Windows virtual environment is in the uploaded archive but was not executable in the Linux review environment. |
| 7 — Release preparation | **Pending owner approval** | Final Git review on the user's local machine, check publication rights and downloaded-source exclusions, fresh install check with internet access, review figure images, then controlled feature-branch commit/push and merge if approved. |

## Original feature-branch history

- `7bb6588` — initial repository commit on `main`.
- `bb7d12d` — official-data extraction, methodology, wage and CPI pipeline, initial tests.
- `55d1980` — README, initial notebook, five figures and summary tables.
- `4ae4229` — local milestone reference updates.
- `434f60a` — packaging/dependency cleanup.

The original `origin/main` shown in the archive remains at `7bb6588`. **Do not assume this local archive proves the live remote is unchanged.** Run `git fetch origin` before publishing.

## Captured-data quality checks

| Check | Reproduced result |
| --- | --- |
| CPI coverage | 8 series × 96 months = 768 observations |
| Official purchasing power | 2 series × 96 months = 192 observations |
| CPI/PPP missing and duplicate month keys | 0 |
| Maximum difference from published rounded PPP | 0.004977 peso, below 0.006 tolerance |
| FIES selected data | 176 observations, 2 geographies × 11 income groups × 8 measures |
| Maximum expenditure-weighted published share deviation | 0.051795 percentage points, below 0.15 tolerance |
| Audited wage events | 8 events, ordered, all rates and increases reconcile |
| Frozen input manifest | 3 dataset SHA-256 hashes checked before replay |
| Unit tests | 28 passed, 0 failed |
| Replaying captured versus frozen data | Matching endpoint and temporal summary metrics |
| Notebook | 9 code cells successfully executed from two project-relative working directories |

## Reproduced findings and different comparison points

- Davao all-items CPI **97.4 → 131.4**; nominal daily benchmark **₱340 → ₱510**; real statutory benchmark **₱349.08 → ₱388.13** (2018 pesos), an **11.19% endpoint increase**.
- Davao cumulative regional CPI change **34.91%** versus **33.74%** for the Philippines, a **1.16-percentage-point** difference.
- Seven below-January-2018-reference months across three episodes. Longest episode **4 months** (April–July 2018); lowest relative reference **July 2018, −2.89%**.
- Maximum prior-peak drawdown **−11.33%**, measured from March 2019 to May 2022. This is **not** the minimum relative to the January 2018 baseline.
- Food-deflated December 2025 wage **₱380.60** in 2018 pesos, **9.37% above its own January 2018 baseline**.
- FIES 2023 Davao food share **58.3%** for first versus **23.9%** for tenth per-capita-income decile; combined food, housing and transport shares **79.8%** versus **57.5%**. These are aggregate expenditure shares, not observed individual purchasing power.

## Local source-recovery and completion record

The uploaded ZIP contained the original `.git` folder, `.venv` and `.venv_clean`, core source code, ignored official raw downloads and partially completed Batch 02 outputs. The continuation preserved existing analysis modules, tests and charts while adding checksum-verified frozen input replay, snapshot construction, an additional FIES comparison figure, improved notebook interpretation, complete data attribution, a project banner, and final reporting documentation. The two Windows environments are excluded from delivery archives; the user's Git history must be retained locally rather than overwritten.

## Final owner-controlled gate

1. Apply the supplied **overlay archive into the existing Git checkout**, leaving `.git` and local environments untouched.
2. Run the frozen pipeline, unit tests, and release verification script in a new local venv with actual package-index access.
3. Review the eight charts and banner, confirm numeric summaries and author name.
4. Check `git status`, `git diff --check`, `git diff --stat`, `git ls-files data/raw` and `.gitignore` before committing.
5. Stage only reviewed sources, normalized tracked snapshots, documented output tables and charts. Do not commit ignored original raw PDFs/API payloads or virtual environments.
6. Create a single or small number of coherent commits on the feature branch, push only after approval, and review GitHub rendering before any merge to `main`.

Detailed commands are in [release checklist](release_checklist.md).
