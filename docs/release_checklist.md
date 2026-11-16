# Local release acceptance checklist

This project remains under the sole authorship of **Cyril James Lunzaga**. Publication must be approved from the local VS Code checkout. These instructions do not grant permission to force-push, merge without review, or publish original PDFs and raw downloads.

## Apply and verify

In PowerShell, from the existing project directory:

```powershell
cd "E:\Machine Learning\The Purchasing Power Trap"
git status --short --branch
git remote -v
```

Back up or commit any unrelated work before applying the completion overlay. Extract the overlay ZIP using `Expand-Archive -Force` into this **same** directory. The overlay has no `.git`, `.venv`, or `.venv_clean` folder, so it does not replace local repository metadata.

For a fresh environment with access to a package index:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe scripts/run_analysis.py --source frozen
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/verify_release.py
```

If a `.venv` already exists, use a separate `.venv_check` directory to test a genuinely new install. Do not claim a clean install merely because a pre-existing virtual environment runs.

To compare against the original downloaded vintage (requires your ignored `data/raw/` files), run:

```powershell
.\.venv\Scripts\python.exe scripts/run_analysis.py --source captured
```

The resulting diagnostic record will show the reproduction mode. The source hashes should match documented archived values; they are not a guarantee that today's live PSA API returns unchanged data.

## Source, figure, and documentation review

- [ ] Every dataset is traced to a PSA or NWPC official URL; original documents are not included in public Git commits.
- [ ] The FIES Table 7 unit of *percent of expenditure within the same income decile* is correctly labeled.
- [ ] The NWPC XI-19 larger-establishment rate and XI-21 smaller-retail transition are transparently described.
- [ ] The project banner is conceptual; plotted figures are computed from the frozen or captured data.
- [ ] The contact sheet contains eight chart panels, each legible at its normal export size.
- [ ] README references resolve, sources are credited, and only Cyril James Lunzaga is credited as author.
- [ ] Frozen and captured pipeline runs produce consistent headline values.
- [ ] 28 or more appropriate tests pass with zero failures, and notebook cells run with actual processed data.
- [ ] Public data attribution, original-order conditions, and any source-specific reuse exceptions were reviewed.

## Controlled Git review

```powershell
git fetch origin
git status --short --branch
git diff --check
git diff --stat
git ls-files data/raw
git ls-files .venv .venv_clean
```

Both `git ls-files` commands should list **nothing**. On the feature branch, stage explicit project paths after reviewing them:

```powershell
git add README.md .gitignore pyproject.toml assets data/frozen data/reference docs notebooks reports scripts src tests
git diff --cached --check
git diff --cached --stat
git status
```

Verify the staged list has no secrets, large original PDFs, virtual environments, unintended user files, or fabricated data. Commit only after checking. **Do not push or merge until explicitly approved by the owner.**
