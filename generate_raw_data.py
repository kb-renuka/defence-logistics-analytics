"""
Generates a deliberately MESSY synthetic dataset for the
'Defence Logistics & Operations Analytics' portfolio project.

Messiness injected on purpose (so the cleaning script has real work to do):
- missing values in several columns
- duplicate rows
- inconsistent category casing/spelling
- outlier numeric values
- mixed date formats
"""
import random
from datetime import date, timedelta
import csv

random.seed(7)

regions = ["Northern Command", "Western Command", "Eastern Command", "Southern Command", "Central Command"]
equipment_types = ["Transport Vehicle", "Communication Equipment", "Medical Unit", "Artillery Support", "Engineering Equipment"]
equipment_types_dirty = equipment_types + ["transport vehicle", "COMMUNICATION EQUIPMENT", "Medical  Unit"]  # casing/spacing issues
maintenance_status = ["Operational", "Under Maintenance", "Awaiting Parts", "Decommissioned"]
delivery_status = ["Delivered", "Delayed", "In Transit", "Cancelled"]

units = [f"Unit-{100+i}" for i in range(0, 30, 3)]

date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]

start = date(2026, 1, 1)

rows = []
for i in range(650):
    unit = random.choice(units)
    region = random.choice(regions)
    equip = random.choice(equipment_types_dirty)
    qty = random.randint(1, 250)
    maint = random.choice(maintenance_status)
    fuel = round(random.uniform(50, 5000), 1)
    supply_req = random.randint(0, 40)
    delivery_date = start + timedelta(days=random.randint(0, 220))
    dfmt = random.choice(date_formats)
    delivery_date_str = delivery_date.strftime(dfmt)
    dstatus = random.choice(delivery_status)
    personnel = random.randint(20, 800)
    readiness = round(random.uniform(0.4, 1.0), 2)
    monthly_cost = round(random.uniform(50000, 2500000), 2)

    # inject missing values (~6% of rows across various columns)
    if random.random() < 0.05:
        fuel = ""
    if random.random() < 0.04:
        maint = ""
    if random.random() < 0.03:
        personnel = ""
    if random.random() < 0.03:
        dstatus = ""

    # inject outliers (~2%)
    if random.random() < 0.02:
        fuel = round(random.uniform(50000, 90000), 1)  # absurd fuel spike
    if random.random() < 0.015:
        monthly_cost = round(random.uniform(20000000, 50000000), 2)  # absurd cost spike

    rows.append({
        "Unit_ID": unit,
        "Region": region,
        "Equipment_Type": equip,
        "Equipment_Quantity": qty,
        "Maintenance_Status": maint,
        "Fuel_Consumption_Litres": fuel,
        "Supply_Requests": supply_req,
        "Delivery_Date": delivery_date_str,
        "Delivery_Status": dstatus,
        "Personnel_Count": personnel,
        "Operational_Readiness": readiness,
        "Monthly_Cost_INR": monthly_cost,
    })

# inject duplicate rows (~3%)
dupes = random.sample(rows, k=int(len(rows) * 0.03))
rows.extend(dupes)
random.shuffle(rows)

fieldnames = list(rows[0].keys())
with open("raw_defence_logistics_data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows (including injected duplicates/missing/outliers) to raw_defence_logistics_data.csv")
