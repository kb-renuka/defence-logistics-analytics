# Tableau plan — Defence Logistics & Operations Analytics

Data source: `cleaned_defence_logistics_data.csv` (same file used for Power BI).
Connect via Tableau Desktop/Public: Connect > Text File.

## Calculated fields to build

```
Delayed Flag
IF [Delivery Status] = "Delayed" THEN 1 ELSE 0 END

Cost per Personnel
IF [Personnel Count] = 0 THEN NULL
ELSE [Monthly Cost Inr] / [Personnel Count] END

Readiness Band
IF [Operational Readiness] < 0.6 THEN "Low"
ELSEIF [Operational Readiness] < 0.8 THEN "Moderate"
ELSE "High" END

MoM Cost Change
(ZN(SUM([Monthly Cost Inr])) - LOOKUP(ZN(SUM([Monthly Cost Inr])), -1))
/ ABS(LOOKUP(ZN(SUM([Monthly Cost Inr])), -1))
-- Table calculation, set "Compute using" = Delivery Month
```

## Worksheets to build

1. **Cost by Region** — horizontal bar, Region on rows, SUM(Monthly Cost Inr) on columns, color by Region
2. **Monthly Cost Trend** — line chart, Delivery Month (continuous) on columns, SUM(Monthly Cost Inr) on rows
3. **Delivery Status Breakdown** — pie or donut, Delivery Status as color/angle
4. **Equipment Readiness Heatmap** — Equipment Type x Maintenance Status, color = COUNT, this is the "advanced visualization" Tableau is preferred for
5. **Readiness by Unit** — bar chart, Unit ID on rows sorted by AVG(Operational Readiness), reference line at overall average

## Dashboard assembly

- Combine 1–3 into an **Overview** dashboard with a Region filter action:
  clicking a bar in "Cost by Region" filters the other two sheets (Dashboard >
  Actions > Filter action, source = Cost by Region, target = all).
- Combine 4–5 into a **Readiness** dashboard with the same filter-action pattern.
- Add a **Region, Equipment Type, Delivery Month** quick filter to both dashboards.

## Why Tableau here specifically (say this if asked)

The equipment readiness heatmap and the click-to-filter dashboard actions are
the two things Tableau does more fluidly than Power BI out of the box — that's
the honest reason to build this piece, not just to tick a box on the JD.
