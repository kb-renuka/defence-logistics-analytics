"""
Data cleaning pipeline: raw_defence_logistics_data.csv -> cleaned_defence_logistics_data.csv

Each step is deliberately explicit and logged, so every transformation can be
explained in an interview (what was wrong, how it was detected, how it was fixed).
"""
import pandas as pd
import numpy as np
import json

report = {}

df = pd.read_csv("raw_defence_logistics_data.csv")
report["rows_raw"] = len(df)

# ---------- 1. Duplicates ----------
dupe_count = df.duplicated().sum()
df = df.drop_duplicates()
report["duplicates_removed"] = int(dupe_count)

# ---------- 2. Standardize categorical text (casing / spacing) ----------
def clean_text(s):
    if pd.isna(s):
        return s
    return " ".join(str(s).strip().split()).title()

for col in ["Equipment_Type", "Maintenance_Status", "Delivery_Status", "Region"]:
    df[col] = df[col].apply(clean_text)

# ---------- 3. Parse mixed date formats ----------
def parse_mixed_date(s):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["Delivery_Date"] = df["Delivery_Date"].apply(parse_mixed_date)
report["unparseable_dates"] = int(df["Delivery_Date"].isna().sum())

# ---------- 4. Missing values ----------
missing_before = df.isna().sum()
report["missing_values_by_column"] = {k: int(v) for k, v in missing_before.items() if v > 0}

# Numeric columns: impute with column median (robust to outliers), flag imputed rows
for col in ["Fuel_Consumption_Litres", "Personnel_Count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    flag_col = f"{col}_was_missing"
    df[flag_col] = df[col].isna()
    median_val = df[col].median()
    df[col] = df[col].fillna(median_val)

# Categorical: impute with 'Unknown' rather than guessing
for col in ["Maintenance_Status", "Delivery_Status"]:
    df[f"{col}_was_missing"] = df[col].isna()
    df[col] = df[col].fillna("Unknown")

# ---------- 5. Outlier detection (IQR method) ----------
outlier_summary = {}
for col in ["Fuel_Consumption_Litres", "Monthly_Cost_INR"]:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    flag_col = f"{col}_outlier"
    df[flag_col] = (df[col] < lower) | (df[col] > upper)
    outlier_summary[col] = {
        "lower_bound": round(float(lower), 2),
        "upper_bound": round(float(upper), 2),
        "outliers_flagged": int(df[flag_col].sum()),
    }
    # cap outliers rather than drop them, so no data is silently lost
    df[col] = df[col].clip(lower=lower, upper=upper)

report["outlier_summary"] = outlier_summary

# ---------- 6. Derived KPI columns ----------
df["Delivery_Month"] = df["Delivery_Date"].dt.to_period("M").astype(str)
df["Cost_Per_Personnel"] = (df["Monthly_Cost_INR"] / df["Personnel_Count"].replace(0, np.nan)).round(2)
df["Readiness_Band"] = pd.cut(
    df["Operational_Readiness"],
    bins=[0, 0.6, 0.8, 1.01],
    labels=["Low", "Moderate", "High"],
    right=False,
)

# ---------- 7. Validation rules ----------
validation_issues = []
if (df["Operational_Readiness"] > 1).any() or (df["Operational_Readiness"] < 0).any():
    validation_issues.append("Operational_Readiness out of [0,1] range")
if (df["Equipment_Quantity"] < 0).any():
    validation_issues.append("Negative Equipment_Quantity found")
if df["Delivery_Date"].isna().any():
    validation_issues.append(f"{df['Delivery_Date'].isna().sum()} rows with unparseable delivery date")
report["validation_issues"] = validation_issues if validation_issues else ["None found"]

report["rows_cleaned"] = len(df)

df.to_csv("cleaned_defence_logistics_data.csv", index=False)

with open("data_quality_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
