"""
Loads cleaned_defence_logistics_data.csv into SQLite, creates a normalized
schema, and runs the analysis queries named in the JD (regional performance,
delivery delays, cost analysis, monthly trends).

Uses SQLite so every query below actually executes against real data ---
the syntax (JOINs, GROUP BY, aggregates, CASE) is standard SQL and transfers
directly to MySQL with only minor dialect changes (documented at the bottom).
"""
import sqlite3
import pandas as pd

df = pd.read_csv("cleaned_defence_logistics_data.csv", parse_dates=["Delivery_Date"])

conn = sqlite3.connect("defence_logistics.db")
cur = conn.cursor()

# ---------- Normalized schema ----------
cur.executescript("""
DROP TABLE IF EXISTS units;
DROP TABLE IF EXISTS logistics;

CREATE TABLE units (
    unit_id TEXT PRIMARY KEY,
    region TEXT NOT NULL
);

CREATE TABLE logistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id TEXT NOT NULL,
    equipment_type TEXT,
    equipment_quantity INTEGER,
    maintenance_status TEXT,
    fuel_consumption_litres REAL,
    supply_requests INTEGER,
    delivery_date TEXT,
    delivery_status TEXT,
    personnel_count INTEGER,
    operational_readiness REAL,
    monthly_cost_inr REAL,
    delivery_month TEXT,
    FOREIGN KEY (unit_id) REFERENCES units(unit_id)
);
""")

units_df = df[["Unit_ID", "Region"]].drop_duplicates(subset=["Unit_ID"], keep="first")
units_df.columns = ["unit_id", "region"]
units_df.to_sql("units", conn, if_exists="append", index=False)

log_cols = {
    "Unit_ID": "unit_id", "Equipment_Type": "equipment_type",
    "Equipment_Quantity": "equipment_quantity", "Maintenance_Status": "maintenance_status",
    "Fuel_Consumption_Litres": "fuel_consumption_litres", "Supply_Requests": "supply_requests",
    "Delivery_Date": "delivery_date", "Delivery_Status": "delivery_status",
    "Personnel_Count": "personnel_count", "Operational_Readiness": "operational_readiness",
    "Monthly_Cost_INR": "monthly_cost_inr", "Delivery_Month": "delivery_month",
}
logistics_df = df[list(log_cols.keys())].rename(columns=log_cols)
logistics_df.to_sql("logistics", conn, if_exists="append", index=False)
conn.commit()

queries = {
    "1. Region-wise total operational cost & avg readiness (JOIN + GROUP BY)": """
        SELECT u.region,
               ROUND(SUM(l.monthly_cost_inr), 2) AS total_cost_inr,
               ROUND(AVG(l.operational_readiness), 3) AS avg_readiness,
               COUNT(*) AS records
        FROM logistics l
        JOIN units u ON u.unit_id = l.unit_id
        GROUP BY u.region
        ORDER BY total_cost_inr DESC;
    """,
    "2. Delivery performance by status (%% of total)": """
        SELECT delivery_status,
               COUNT(*) AS n,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM logistics), 1) AS pct
        FROM logistics
        GROUP BY delivery_status
        ORDER BY n DESC;
    """,
    "3. Delayed deliveries by region (JOIN + filter)": """
        SELECT u.region, COUNT(*) AS delayed_count
        FROM logistics l
        JOIN units u ON u.unit_id = l.unit_id
        WHERE l.delivery_status = 'Delayed'
        GROUP BY u.region
        ORDER BY delayed_count DESC;
    """,
    "4. Monthly cost trend": """
        SELECT delivery_month, ROUND(SUM(monthly_cost_inr), 2) AS total_cost_inr
        FROM logistics
        GROUP BY delivery_month
        ORDER BY delivery_month;
    """,
    "5. Equipment needing attention (maintenance backlog)": """
        SELECT equipment_type, maintenance_status, COUNT(*) AS n
        FROM logistics
        WHERE maintenance_status IN ('Under Maintenance', 'Awaiting Parts')
        GROUP BY equipment_type, maintenance_status
        ORDER BY n DESC
        LIMIT 8;
    """,
    "6. Units with below-average operational readiness (subquery)": """
        SELECT unit_id, ROUND(AVG(operational_readiness), 3) AS avg_readiness
        FROM logistics
        GROUP BY unit_id
        HAVING avg_readiness < (SELECT AVG(operational_readiness) FROM logistics)
        ORDER BY avg_readiness ASC
        LIMIT 8;
    """,
}

lines = []
for title, q in queries.items():
    lines.append(f"\n-- {title}\n")
    lines.append(q.strip() + "\n")
    result = pd.read_sql_query(q, conn)
    lines.append("/* Sample result:\n" + result.to_string(index=False) + "\n*/\n")
    print(f"\n=== {title} ===")
    print(result.to_string(index=False))

with open("schema_and_queries.sql", "w") as f:
    f.write("-- Defence Logistics & Operations Analytics: Schema + Queries\n")
    f.write("-- SQLite syntax (used for local execution/testing).\n")
    f.write("-- MySQL notes: AUTOINCREMENT -> AUTO_INCREMENT; 100.0 division is identical.\n\n")
    f.write("""CREATE TABLE units (
    unit_id VARCHAR(20) PRIMARY KEY,
    region VARCHAR(50) NOT NULL
);

CREATE TABLE logistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_id VARCHAR(20) NOT NULL,
    equipment_type VARCHAR(50),
    equipment_quantity INT,
    maintenance_status VARCHAR(30),
    fuel_consumption_litres DECIMAL(10,1),
    supply_requests INT,
    delivery_date DATE,
    delivery_status VARCHAR(20),
    personnel_count INT,
    operational_readiness DECIMAL(4,3),
    monthly_cost_inr DECIMAL(12,2),
    delivery_month VARCHAR(7),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id)
);
""")
    f.writelines(lines)

conn.close()
print("\nWrote defence_logistics.db and schema_and_queries.sql (with sample results as comments)")
