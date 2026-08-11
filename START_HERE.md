# START HERE — Defence Logistics Project Setup Guide

## 1. Download
Save every file from the chat into one folder on your computer, e.g. `Defence-Logistics-Project/`.

## 2. Open the Excel file
Double-click `Defence_Logistics_Analysis.xlsx`. Opens directly in Excel — nothing to import.
This covers your Advanced Excel requirement: INDEX/MATCH, SUMIFS, native table.

## 3. Add PivotTable + Dynamic Arrays (inside that same Excel file)
- Click inside the `Cleaned_Data` table → **Insert > PivotTable**.
- Open `Dynamic_Arrays_and_XLOOKUP.md`, copy those formulas into a new sheet.
  (They only work in real Excel 365 — that's why they weren't pre-built into the file.)

## 4. Build Power BI
- Install **Power BI Desktop** (free, Microsoft).
- **Get Data > Text/CSV** → select `cleaned_defence_logistics_data.csv`.
- **Transform Data > Advanced Editor** → paste in the code from `Power_Query_ETL.pq`.
- **Modeling > New Measure** → paste each measure from `DAX_Measures.txt` one at a time.
- Build the 4 pages listed at the bottom of `DAX_Measures.txt`.

## 5. Build Tableau (optional, do last)
- Install **Tableau Desktop** or use **Tableau Public** (free).
- Connect to the same `cleaned_defence_logistics_data.csv`.
- Open `Tableau_Plan.md` and build the calculated fields + worksheets listed there.

## 6. Push to GitHub
- Create a repo, e.g. `defence-logistics-analytics`.
- Upload everything: CSVs, `.py` scripts, `.sql` file, `.xlsx`, `.pq`, `.txt`, `.md` files.
- Add a screenshot of your finished Power BI dashboard.
- This repo link goes on your resume next to the project bullet.

## 7. Update resume / LinkedIn
- Use the resume bullets already written in `README.md`.
- Add the GitHub link.
- Only list Power BI / Tableau as skills once you've actually built them in steps 4–5 — not before.

---
If you get stuck on any step — especially installing or using Power BI / Tableau — come back and ask, and I'll walk through it in more detail.
