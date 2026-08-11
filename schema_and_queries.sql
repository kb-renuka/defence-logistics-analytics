-- Defence Logistics & Operations Analytics: Schema + Queries
-- SQLite syntax (used for local execution/testing).
-- MySQL notes: AUTOINCREMENT -> AUTO_INCREMENT; 100.0 division is identical.

CREATE TABLE units (
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

-- 1. Region-wise total operational cost & avg readiness (JOIN + GROUP BY)
SELECT u.region,
               ROUND(SUM(l.monthly_cost_inr), 2) AS total_cost_inr,
               ROUND(AVG(l.operational_readiness), 3) AS avg_readiness,
               COUNT(*) AS records
        FROM logistics l
        JOIN units u ON u.unit_id = l.unit_id
        GROUP BY u.region
        ORDER BY total_cost_inr DESC;
/* Sample result:
         region  total_cost_inr  avg_readiness  records
Eastern Command    428090338.55          0.690      322
Western Command    351635167.13          0.723      277
Central Command     69597915.82          0.669       51
*/

-- 2. Delivery performance by status (%% of total)
SELECT delivery_status,
               COUNT(*) AS n,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM logistics), 1) AS pct
        FROM logistics
        GROUP BY delivery_status
        ORDER BY n DESC;
/* Sample result:
delivery_status   n  pct
        Delayed 179 27.5
      Cancelled 159 24.5
     In Transit 157 24.2
      Delivered 143 22.0
        Unknown  12  1.8
*/

-- 3. Delayed deliveries by region (JOIN + filter)
SELECT u.region, COUNT(*) AS delayed_count
        FROM logistics l
        JOIN units u ON u.unit_id = l.unit_id
        WHERE l.delivery_status = 'Delayed'
        GROUP BY u.region
        ORDER BY delayed_count DESC;
/* Sample result:
         region  delayed_count
Eastern Command             90
Western Command             71
Central Command             18
*/

-- 4. Monthly cost trend
SELECT delivery_month, ROUND(SUM(monthly_cost_inr), 2) AS total_cost_inr
        FROM logistics
        GROUP BY delivery_month
        ORDER BY delivery_month;
/* Sample result:
delivery_month  total_cost_inr
       2026-01    107800174.12
       2026-02    106787042.36
       2026-03    112769024.64
       2026-04    135565753.48
       2026-05    135113766.99
       2026-06    123072703.14
       2026-07     93161252.51
       2026-08     35053704.27
*/

-- 5. Equipment needing attention (maintenance backlog)
SELECT equipment_type, maintenance_status, COUNT(*) AS n
        FROM logistics
        WHERE maintenance_status IN ('Under Maintenance', 'Awaiting Parts')
        GROUP BY equipment_type, maintenance_status
        ORDER BY n DESC
        LIMIT 8;
/* Sample result:
         equipment_type maintenance_status  n
      Transport Vehicle  Under Maintenance 41
Communication Equipment     Awaiting Parts 37
Communication Equipment  Under Maintenance 37
      Transport Vehicle     Awaiting Parts 37
           Medical Unit  Under Maintenance 36
           Medical Unit     Awaiting Parts 31
      Artillery Support  Under Maintenance 25
  Engineering Equipment     Awaiting Parts 22
*/

-- 6. Units with below-average operational readiness (subquery)
SELECT unit_id, ROUND(AVG(operational_readiness), 3) AS avg_readiness
        FROM logistics
        GROUP BY unit_id
        HAVING avg_readiness < (SELECT AVG(operational_readiness) FROM logistics)
        ORDER BY avg_readiness ASC
        LIMIT 8;
/* Sample result:
 unit_id  avg_readiness
Unit-127          0.664
Unit-118          0.669
Unit-121          0.677
Unit-124          0.681
Unit-106          0.692
*/
