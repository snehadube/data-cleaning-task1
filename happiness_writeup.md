# Data Cleaning Write-Up — World Happiness Report (2015-2019)

## Dataset
5 separate yearly CSV files from Kaggle (2015.csv – 2019.csv), 155-158 countries each, merged into one combined dataset of 782 rows (country + year).

## Issues Found & How Each Was Resolved

| # | Issue | How Found | Resolution |
|---|-------|-----------|------------|
| 1 | **Inconsistent column names across years** for the same metric (e.g. `Trust (Government Corruption)` in 2015, `Trust..Government.Corruption.` in 2017, `Perceptions of corruption` in 2018-19) | Printed `df.columns` for each year and compared | Built a mapping dictionary translating every year's column names into one standard schema (`country`, `score`, `gdp_per_capita`, `corruption_perception`, etc.) before merging |
| 2 | **Different column sets per year** — 2015/2016 include `Region`, `Standard Error`/confidence intervals, and `Dystopia Residual` that 2017-2019 don't have | Compared column lists directly | Kept only the 9 "core" columns present in *every* year, so the merged dataset is fully comparable across all 5 years rather than full of NaNs for columns some years never collected |
| 3 | **Inconsistent country names across years** (e.g. `Macedonia` → `North Macedonia`, `North Cyprus` → `Northern Cyprus`, `Trinidad and Tobago` → `Trinidad & Tobago`) — same country, different spelling in different years | Compared the set of country names in 2015 vs 2019 with a set difference | Replaced 10 variant names with one standard spelling per country, so year-over-year trend analysis doesn't wrongly treat one country as two |
| 4 | **1 missing value** — United Arab Emirates' `corruption_perception` in 2018 | `df.isnull().sum()` | Imputed with that year's median value (0.082), since it was a single isolated gap, not a systemic missing-data problem |
| 5 | **Wrong/mixed data types** — rank appeared as float in some merges, year needed enforcing as integer | `df.info()` after merge | Cast `rank` and `year` to `int`, all score/metric columns to `float` |
| 6 | **Duplicate (country, year) rows** | Checked `duplicated(subset=['country','year'])` | Found 0 — but the check was still run, since assuming no duplicates without checking is itself a data-quality risk |

## Why Merge Instead of Cleaning Each File Separately
Cleaning each year in isolation would miss the real problem: the *same* underlying data was labeled differently every year. Standardizing column names and country spellings **before** merging is what makes a genuine 5-year trend analysis possible (e.g. tracking how a country's happiness score changed from 2015 to 2019) — this is the core value-add of combining the files rather than treating them as five separate cleaning exercises.

## Null-Handling Rationale
- Only one missing value existed in the entire 5-year dataset (UAE, 2018) — imputed with that year's median since dropping the whole country-year row would lose otherwise complete data for no good reason.
- No columns had heavy (>10%) missingness requiring a drop/flag decision in this dataset — a very different situation from datasets like Titanic where ~77% of a column can be missing.

## Verification After Cleaning
- `isnull().sum()` → 0 across all 10 columns
- `duplicated(subset=['country','year'])` → 0
- Row counts per year confirmed close to original counts (155-158), confirming no accidental data loss during the merge
- Country name standardization confirmed no more spelling-variant duplicates when grouping by country across years

## Final Output
`happiness_cleaned_2015_2019.csv` / `.xlsx` — 782 rows × 10 columns: `country, rank, score, gdp_per_capita, social_support, life_expectancy, freedom, corruption_perception, generosity, year`. Ready for year-over-year comparison, correlation analysis (e.g. GDP vs happiness score), or ranking-change analysis per country.
