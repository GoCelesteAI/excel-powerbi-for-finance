-- SQL for Finance — Episode 2: Filter, sort, pick
-- =====================================================================
-- The four queries shown in the episode plus extras. Run from inside the
-- sqlite3 shell against atlasparts.db, or via:
--   sqlite3 atlasparts.db < ep02_filter_sort_pick.sql

.headers on
.mode column

-- 1. WHERE: customers in the US (the way you write it first)
SELECT customer_name, country, region
FROM   customers
WHERE  country = 'US'
LIMIT  5;

-- How many came back? 25 — but the data has spelling drift.
SELECT COUNT(*) FROM customers WHERE country = 'US';

-- Reveal the drift:
SELECT DISTINCT country FROM customers ORDER BY country;

-- The corrected version that catches all spellings — 30 rows.
SELECT COUNT(*)
FROM   customers
WHERE  country IN ('US', 'USA', 'us', 'United States of America');

-- 2. WHERE with operators: orders over $10K — 292 of 2,242 total.
SELECT COUNT(*)
FROM   sales_orders
WHERE  CAST(order_total AS REAL) > 10000;

-- The same filter, showing actual rows.
SELECT order_id, order_date, customer_id, order_total
FROM   sales_orders
WHERE  CAST(order_total AS REAL) > 10000
LIMIT  5;

-- BETWEEN is inclusive. Mid-band orders.
SELECT order_id, ROUND(CAST(order_total AS REAL), 2) AS amt
FROM   sales_orders
WHERE  CAST(order_total AS REAL) BETWEEN 5000 AND 10000
LIMIT  5;

-- 3. ORDER BY: biggest first.
SELECT order_id, customer_id, ROUND(CAST(order_total AS REAL), 2) AS amt
FROM   sales_orders
WHERE  CAST(order_total AS REAL) > 10000
ORDER  BY amt DESC
LIMIT  5;

-- Multi-column sort — status alphabetical, then amount DESC inside each.
SELECT order_id, status, ROUND(CAST(order_total AS REAL), 2) AS amt
FROM   sales_orders
WHERE  CAST(order_total AS REAL) > 22000
ORDER  BY status, amt DESC;

-- 4. LIMIT: top 20 by amount.
SELECT order_id, customer_id, ROUND(CAST(order_total AS REAL), 2) AS amt
FROM   sales_orders
ORDER  BY CAST(order_total AS REAL) DESC
LIMIT  20;
