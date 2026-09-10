# Data Cleaning & Preprocessing - World Happiness Report (2015-2019)

## Objective
Clean and merge 5 years of the World Happiness Report dataset (2015-2019) 
into one consistent dataset, fixing inconsistent column names, country 
name variants, missing values, and data types.

## Files
- `cleaning_script.py` - Full Python cleaning & merging pipeline
- `happiness_cleaned_2015_2019.csv` - Final cleaned dataset (782 rows)
- `happiness_cleaned.xlsx` - Same data in Excel with a Change Log sheet
- `happiness_change_log.txt` - List of every fix applied
- `happiness_writeup.md` - Write-up of issues found and how they were resolved

## Tools Used
Python, Pandas

## Key Issues Fixed
1. Inconsistent column names across yearly files (standardized into one schema)
2. Country name mismatches across years (e.g. Macedonia -> North Macedonia)
3. Missing value (1 row) - imputed with column median
4. Data type inconsistencies - enforced correct int/float types
5. Verified 0 nulls and 0 duplicates after cleaning

## Result
782 rows x 10 columns, ready for year-over-year happiness trend analysis.
