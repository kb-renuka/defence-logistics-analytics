# Defence Logistics & Operations Analytics — Portfolio Project

Synthetic dataset (not real/classified data) modeling unit-level defence logistics:
equipment status, fuel consumption, delivery performance, personnel, cost, and
operational readiness across 5 regional commands.

## What's in this project

| Layer | File | Demonstrates |
|---|---|---|
| Raw data | `raw_defence_logistics_data.csv` | 669 rows with deliberately injected duplicates, missing values, inconsistent casing, mixed date formats, outliers |
| Data cleaning | `clean_data.py` → `cleaned_defence_logistics_data.csv` | Pandas: dedup, text normalization, mixed-format date parsing, median imputation with missing-flags, IQR outlier detection + capping, derived KPIs, validation rules |
| Data quality report | `data_quality_report.json` | Auditable before/after numbers (19 duplicates removed, 82 missing values imputed, 26 outliers flagged) |
| SQL | `sql_analysis.py` → `defence_logistics.db`, `schema_and_queries.sql` | Normalized schema (`units`, `logistics`), JOINs, GROUP BY, subqueries, % calculations — region cost, delivery delays, maintenance backlog, readiness outliers |
| Excel | `Defence_Logistics_Analysis.xlsx` | Native Excel Table (PivotTable-ready source), INDEX/MATCH lookup, SUMIFS/AVERAGEIFS/COUNTIFS regional summary, bar + pie charts |
| Interactive dashboard | *(rendered inline above)* | HTML/Chart.js dashboard — KPI cards, region filter, cost/trend/status/equipment charts — a working stand-in for the Power BI visual layer, built from real aggregated numbers |
| Power BI | `Power_Query_ETL.pq`, `DAX_Measures.txt` | Real M code (ETL) + real DAX measures + 4-page layout plan — paste both into Power BI Desktop |
| Dynamic Arrays / XLOOKUP | `Dynamic_Arrays_and_XLOOKUP.md` | Working formulas for real Excel 365 (kept out of the .xlsx — see file for why) |
| Tableau | `Tableau_Plan.md` | Calculated fields, worksheets, dashboard actions |

## How to run it yourself

```bash
python3 generate_raw_data.py   # creates the messy raw CSV
python3 clean_data.py          # cleans it, writes report
python3 sql_analysis.py        # loads to SQLite, runs queries, writes .sql file
python3 build_excel.py         # builds the Excel workbook
```

## Known simplifications (say this if asked — it's a strength, not a weakness, to be upfront)

- Data is synthetic, generated with a fixed random seed for reproducibility — not real military data.
- The SQL layer treats each `Unit_ID` as belonging to one fixed region (real-world correct), while the raw generator randomized region per-record — so SQL and Excel regional totals won't match exactly. In a real dataset this wouldn't occur; it's a known artifact of synthetic generation, not a modeling bug.
- `XLOOKUP` was intentionally avoided in favor of `INDEX/MATCH` — more broadly compatible across Excel versions and what most enterprise environments still standardize on. Worth mentioning if asked why.

## To finish the Power BI layer yourself (~1 evening)

1. Open Power BI Desktop → Get Data → Text/CSV → `cleaned_defence_logistics_data.csv`.
2. Home → Transform Data to open Power Query — this is where you'd point to
   "Power Query used for ETL" on your resume (you can also re-derive a couple of
   the Python cleaning steps here, e.g. trimming text columns, to show you can do
   it either way).
3. Build these DAX measures (Modeling → New Measure):
   ```
   Total Cost = SUM(logistics[Monthly_Cost_INR])
   Avg Readiness = AVERAGE(logistics[Operational_Readiness])
   Delayed % = DIVIDE(CALCULATE(COUNTROWS(logistics), logistics[Delivery_Status]="Delayed"), COUNTROWS(logistics))
   MoM Cost Change = VAR CurM = [Total Cost] VAR PrevM = CALCULATE([Total Cost], DATEADD(logistics[Delivery_Date], -1, MONTH)) RETURN DIVIDE(CurM - PrevM, PrevM)
   ```
4. Four pages: **Executive Overview** (KPI cards + region map), **Logistics Analysis**
   (delivery status breakdown, delay trend), **Equipment Readiness** (maintenance
   status by equipment type), **Trends & Insights** (monthly line chart + a text box
   with 3 written insights you pulled from the SQL queries above).
5. Add slicers: Region, Equipment_Type, Delivery_Month, Delivery_Status.

## Resume bullets (only keep ones for parts you actually did)

> **Defence Logistics & Operations Analytics Dashboard** — *Python, Pandas, SQL, Excel, Power BI*
> - Built an end-to-end analytics pipeline cleaning and validating a 650+ record synthetic logistics dataset — deduplication, missing-value imputation, IQR-based outlier detection, and rule-based validation.
> - Designed a normalized SQL schema and wrote JOIN/GROUP BY/subquery analyses covering regional cost, delivery delay rates, and equipment maintenance backlog.
> - Built an Excel reporting layer with a native PivotTable-ready dataset, INDEX/MATCH lookups, and SUMIFS/COUNTIFS regional KPI summaries with linked charts.
> - *(if you complete the Power BI step)* Built a 4-page interactive Power BI dashboard with DAX measures, slicers, and month-over-month trend analysis; identified [name 2-3 real findings once you run it].

## Which skills to list on your resume — direct answer

Only list what this project makes you able to *defend in an interview*. Based on
what's actually built right now:

**Solid to list immediately:**
- Python (Pandas) — data cleaning/validation
- SQL — joins, aggregation, schema design
- Advanced Excel — INDEX/MATCH, SUMIFS/COUNTIFS/AVERAGEIFS, PivotTable-ready tables, charting
- Data validation & data quality auditing

**Add only after you actually do the Power BI step:**
- Power BI, DAX, Power Query — don't list these yet; they're the one layer not built here

**Don't list yet (per the original plan, deprioritized):**
- Tableau, VBA — skip unless you specifically build something in them

Rule of thumb: if you can't explain *why* you chose IQR over z-score for outliers,
or *why* INDEX/MATCH over XLOOKUP, don't put the underlying skill on the resume —
this project is set up so you can answer both.
