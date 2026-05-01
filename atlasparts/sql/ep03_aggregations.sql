-- SQL for Finance — Episode 3: Aggregations + GROUP BY
-- =====================================================================
-- The pivot-table replacement: COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING.
-- Run from inside the sqlite3 shell against atlasparts.db, or via:
--   sqlite3 atlasparts.db < ep03_aggregations.sql

.headers on
.mode column

-- 1. The five aggregates: a one-row summary of the whole sales_orders table.
SELECT COUNT(*)                                      AS orders,
       ROUND(SUM(CAST(order_total AS REAL)), 0)      AS revenue,
       ROUND(AVG(CAST(order_total AS REAL)), 2)      AS avg_order,
       ROUND(MIN(CAST(order_total AS REAL)), 2)      AS smallest,
       ROUND(MAX(CAST(order_total AS REAL)), 2)      AS largest
FROM   sales_orders;

-- 2. GROUP BY: orders by status — the single-table pivot table.
SELECT status,
       COUNT(*)                                      AS orders,
       ROUND(SUM(CAST(order_total AS REAL)), 0)      AS total
FROM   sales_orders
GROUP  BY status
ORDER  BY total DESC;

-- 3. GROUP BY across tables: revenue by region (preview of Ep4 JOINs).
SELECT c.region,
       COUNT(*)                                      AS orders,
       ROUND(SUM(CAST(o.order_total AS REAL)), 0)    AS revenue
FROM   sales_orders o
JOIN   customers   c USING (customer_id)
GROUP  BY c.region
ORDER  BY revenue DESC
LIMIT  8;

-- 4. The debit/credit trap: Revenue debits = $0 because revenue is credit-normal.
SELECT account_type,
       COUNT(*)                                      AS entries,
       ROUND(SUM(CAST(debit AS REAL)), 0)            AS total_debits
FROM   gl_journal
JOIN   chart_of_accounts USING (account_id)
GROUP  BY account_type
ORDER  BY total_debits DESC;

-- 5. HAVING: regions with revenue > $1M (filter groups, not rows).
SELECT c.region,
       ROUND(SUM(CAST(o.order_total AS REAL)), 0)    AS revenue
FROM   sales_orders o
JOIN   customers   c USING (customer_id)
GROUP  BY c.region
HAVING SUM(CAST(o.order_total AS REAL)) > 1000000
ORDER  BY revenue DESC;
