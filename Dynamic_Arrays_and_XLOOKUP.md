# Dynamic array & XLOOKUP formulas for Excel

These formulas are **not baked into Defence_Logistics_Analysis.xlsx**. The
reason is technical, not a shortcut: this workbook is recalculated here using
LibreOffice, which cannot evaluate `UNIQUE`, `FILTER`, `SORT`, `SEQUENCE`, or
`XLOOKUP` — a file containing them would either error or silently truncate to
one cell. In real Excel (365 or 2021+) these work natively. Paste them
directly into `Cleaned_Data` or a new sheet in your own copy.

## UNIQUE — distinct list of equipment types
```
=UNIQUE(Cleaned_Data!C5:C654)
```

## SORT + UNIQUE — distinct regions, alphabetical
```
=SORT(UNIQUE(Cleaned_Data!B5:B654))
```

## FILTER — all delayed deliveries in Southern Command
```
=FILTER(Cleaned_Data!A5:L654,
  (Cleaned_Data!B5:B654="Southern Command") * (Cleaned_Data!I5:I654="Delayed"))
```

## XLOOKUP — equipment criticality (equivalent to the INDEX/MATCH already in Lookup_Demo)
```
=XLOOKUP(A2, Lookup_Demo!$A$5:$A$9, Lookup_Demo!$C$5:$C$9, "Not found")
```
Functionally identical to the `INDEX/MATCH` version already in the workbook —
`XLOOKUP` is newer syntax, `INDEX/MATCH` is the version guaranteed to work in
any Excel version and in automated/scripted pipelines. Knowing both, and why
you'd pick one over the other, is the actual skill being tested.

## Dynamic array KPI: top 5 units by cost (SORT + FILTER combined)
```
=SORT(UNIQUE(FILTER(Cleaned_Data!A5:A654, Cleaned_Data!L5:L654>0)), 1, -1)
```
