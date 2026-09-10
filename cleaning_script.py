"""
STEP 2 - CLEAN & MERGE (World Happiness Report, 2015-2019)
-------------------------------------------------------------
GOAL: Combine 5 separate yearly files into ONE clean dataset that can be
used for year-over-year analysis (e.g. "how did India's happiness rank
change from 2015 to 2019?").

WHY MERGE INSTEAD OF CLEANING EACH FILE SEPARATELY?
Each year's file uses different column names for the SAME underlying data
(e.g. "Trust (Government Corruption)" in 2015 vs "Perceptions of corruption"
in 2019). If we don't standardize these into one common schema, we can't
compare years side by side - which defeats the purpose of having 5 years
of data in the first place.
"""
import pandas as pd

change_log = []
def log(msg):
    change_log.append(msg)
    print(msg)

# ------------------------------------------------------------------
# STEP A: Define a mapping from each year's messy column names ->
# ONE standard set of column names we will use across all years.
# WHY: This is the core fix for "inconsistent format" - same concept,
# different labels, across files.
# ------------------------------------------------------------------
STANDARD_COLS = {
    "Country": "country",
    "Country or region": "country",
    "Region": "region",
    "Happiness Rank": "rank",
    "Happiness.Rank": "rank",
    "Overall rank": "rank",
    "Happiness Score": "score",
    "Happiness.Score": "score",
    "Score": "score",
    "Economy (GDP per Capita)": "gdp_per_capita",
    "Economy..GDP.per.Capita.": "gdp_per_capita",
    "GDP per capita": "gdp_per_capita",
    "Family": "social_support",
    "Social support": "social_support",
    "Health (Life Expectancy)": "life_expectancy",
    "Health..Life.Expectancy.": "life_expectancy",
    "Healthy life expectancy": "life_expectancy",
    "Freedom": "freedom",
    "Freedom to make life choices": "freedom",
    "Trust (Government Corruption)": "corruption_perception",
    "Trust..Government.Corruption.": "corruption_perception",
    "Perceptions of corruption": "corruption_perception",
    "Generosity": "generosity",
}
log("Defined a standard column-name mapping so the same real-world concept "
    "(e.g. GDP per capita) has ONE consistent name across all 5 files")

# ------------------------------------------------------------------
# STEP B: Load each year, rename columns to the standard set, keep
# only the columns that exist in every year (a common schema), and
# tag each row with its Year. Drop columns that only exist in some
# years (Region, confidence intervals, Dystopia Residual) rather than
# forcing empty values into years that never had them.
# WHY: Better to keep a clean, comparable "core" dataset than a wide
# dataset full of NaNs for columns only some years collected.
# ------------------------------------------------------------------
CORE_COLS = ["country", "rank", "score", "gdp_per_capita", "social_support",
             "life_expectancy", "freedom", "corruption_perception", "generosity"]

frames = []
for yr in [2015, 2016, 2017, 2018, 2019]:
    df = pd.read_csv(f"{yr}.csv")
    before_cols = list(df.columns)
    df = df.rename(columns=STANDARD_COLS)
    missing_in_year = [c for c in CORE_COLS if c not in df.columns]
    df = df[[c for c in CORE_COLS if c in df.columns]]
    df["year"] = yr
    frames.append(df)
    log(f"{yr}: renamed columns to standard schema "
        f"({'no columns missing' if not missing_in_year else 'missing: ' + str(missing_in_year)})")

combined = pd.concat(frames, ignore_index=True)
log(f"Merged all 5 yearly files into one dataset: {combined.shape[0]} rows total "
    f"(one row per country per year)")

# ------------------------------------------------------------------
# STEP C: Fix inconsistent country names across years.
# WHY: Without this, the SAME country is treated as two different
# countries in different years, which breaks any trend/comparison
# analysis (e.g. "Macedonia" 2015-2017 vs "North Macedonia" 2018-2019
# would look like the country disappeared and a new one appeared).
# ------------------------------------------------------------------
NAME_FIXES = {
    "Macedonia": "North Macedonia",
    "North Cyprus": "Northern Cyprus",
    "Trinidad and Tobago": "Trinidad & Tobago",
}
affected = combined["country"].isin(NAME_FIXES.keys()).sum()
combined["country"] = combined["country"].replace(NAME_FIXES)
log(f"Standardized {affected} country name variants to match a single spelling "
    f"per country (e.g. 'Macedonia' -> 'North Macedonia') so year-over-year "
    f"comparisons for the same country are not broken by spelling differences")

# ------------------------------------------------------------------
# STEP D: Handle the 1 missing value (2018, UAE corruption_perception).
# WHY median-by-column, not a single global fill: corruption_perception
# scores vary a lot by country; filling with the column's overall median
# for that year is a reasonable, defensible estimate for one data point,
# clearly better than leaving a NaN that would break calculations.
# ------------------------------------------------------------------
missing_before = combined["corruption_perception"].isnull().sum()
median_2018 = combined.loc[combined["year"] == 2018, "corruption_perception"].median()
combined["corruption_perception"] = combined["corruption_perception"].fillna(median_2018)
log(f"Imputed {missing_before} missing 'corruption_perception' value (UAE, 2018) "
    f"with that year's median ({median_2018:.3f}) since it was a single isolated "
    f"missing value, not a systemic gap")

# ------------------------------------------------------------------
# STEP E: Check & remove duplicates (same country + year appearing twice
# would double-count that country-year in any aggregation).
# ------------------------------------------------------------------
dupes = combined.duplicated(subset=["country", "year"]).sum()
combined = combined.drop_duplicates(subset=["country", "year"])
log(f"Checked for duplicate (country, year) pairs: found and removed {dupes}")

# ------------------------------------------------------------------
# STEP F: Enforce correct data types.
# WHY: rank should be a whole number (int), scores/metrics are floats.
# Mixed/text types would break any numeric analysis or plotting later.
# ------------------------------------------------------------------
combined["rank"] = combined["rank"].astype(int)
combined["year"] = combined["year"].astype(int)
numeric_cols = ["score", "gdp_per_capita", "social_support", "life_expectancy",
                 "freedom", "corruption_perception", "generosity"]
for c in numeric_cols:
    combined[c] = pd.to_numeric(combined[c], errors="coerce")
log("Enforced correct data types: 'rank' and 'year' as integers, "
    "all score/metric columns as floats")

# ------------------------------------------------------------------
# STEP G: Final verification - re-run the same checks as Step 1
# ------------------------------------------------------------------
print("\n--- FINAL VERIFICATION ---")
print("Shape:", combined.shape)
print("Nulls:\n", combined.isnull().sum())
print("Duplicate (country, year) pairs:", combined.duplicated(subset=["country","year"]).sum())
print("Countries per year:\n", combined.groupby("year")["country"].nunique())

# ------------------------------------------------------------------
# SAVE
# ------------------------------------------------------------------
combined.to_csv("happiness_cleaned_2015_2019.csv", index=False)

with open("change_log.txt", "w") as f:
    f.write("DATA CLEANING CHANGE LOG - World Happiness Report (2015-2019)\n")
    f.write("=" * 60 + "\n\n")
    for i, entry in enumerate(change_log, 1):
        f.write(f"{i}. {entry}\n")

print(f"\nSaved: happiness_cleaned_2015_2019.csv ({combined.shape[0]} rows), change_log.txt")
