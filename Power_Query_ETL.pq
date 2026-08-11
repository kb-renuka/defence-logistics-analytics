// Power Query M — Defence Logistics ETL
// Paste into: Power BI Desktop > Home > Transform Data > Advanced Editor
// (or Excel > Data > Get Data > Launch Power Query Editor > Advanced Editor)
// Mirrors clean_data.py so you can explain the same logic in either tool.

let
    Source = Csv.Document(
        File.Contents("cleaned_defence_logistics_data.csv"),
        [Delimiter=",", Columns=17, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // 1. Set correct types (Power Query is picky — do this before anything else)
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"Unit_ID", type text},
        {"Region", type text},
        {"Equipment_Type", type text},
        {"Equipment_Quantity", Int64.Type},
        {"Maintenance_Status", type text},
        {"Fuel_Consumption_Litres", type number},
        {"Supply_Requests", Int64.Type},
        {"Delivery_Date", type date},
        {"Delivery_Status", type text},
        {"Personnel_Count", Int64.Type},
        {"Operational_Readiness", type number},
        {"Monthly_Cost_INR", type number}
    }),

    // 2. Trim and standardize text casing (equivalent to Python's clean_text())
    TrimmedText = Table.TransformColumns(TypedColumns, {
        {"Region", Text.Proper, type text},
        {"Equipment_Type", Text.Proper, type text},
        {"Maintenance_Status", Text.Proper, type text},
        {"Delivery_Status", Text.Proper, type text}
    }),

    // 3. Remove exact duplicate rows
    RemovedDuplicates = Table.Distinct(TrimmedText),

    // 4. Fill missing categorical values with "Unknown" (matches clean_data.py step 4)
    FilledMaintenance = Table.ReplaceValue(RemovedDuplicates, null, "Unknown", Replacer.ReplaceValue, {"Maintenance_Status"}),
    FilledStatus = Table.ReplaceValue(FilledMaintenance, null, "Unknown", Replacer.ReplaceValue, {"Delivery_Status"}),

    // 5. Add Delivery_Month for time-based aggregation (matches Delivery_Month column)
    AddedMonth = Table.AddColumn(FilledStatus, "Delivery_Month", each Date.ToText([Delivery_Date], "yyyy-MM"), type text),

    // 6. Add Readiness_Band (matches pd.cut bins in clean_data.py)
    AddedReadinessBand = Table.AddColumn(AddedMonth, "Readiness_Band", each
        if [Operational_Readiness] < 0.6 then "Low"
        else if [Operational_Readiness] < 0.8 then "Moderate"
        else "High", type text
    ),

    // 7. Add Cost_Per_Personnel (guard divide-by-zero, matches Python's .replace(0, NaN))
    AddedCostPerPersonnel = Table.AddColumn(AddedReadinessBand, "Cost_Per_Personnel", each
        if [Personnel_Count] = 0 then null
        else Number.Round([Monthly_Cost_INR] / [Personnel_Count], 2), type nullable number
    ),

    // 8. Final column reorder for clarity
    FinalColumns = Table.ReorderColumns(AddedCostPerPersonnel, {
        "Unit_ID","Region","Equipment_Type","Equipment_Quantity","Maintenance_Status",
        "Fuel_Consumption_Litres","Supply_Requests","Delivery_Date","Delivery_Month",
        "Delivery_Status","Personnel_Count","Operational_Readiness","Readiness_Band",
        "Monthly_Cost_INR","Cost_Per_Personnel"
    })
in
    FinalColumns
