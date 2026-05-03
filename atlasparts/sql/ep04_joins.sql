-- SQL for Finance — Episode 4: JOINs in Depth
-- =====================================================================
-- INNER, LEFT, RIGHT, and the wrong-cardinality trap.
-- Run from inside the sqlite3 shell against atlasparts.db, or via:
--   sqlite3 atlasparts.db < ep04_joins.sql

.headers on
.mode column

-- 1. INNER JOIN: orders with their customer name and region.
SELECT o.order_id,
       c.customer_name,
       c.region,
       o.order_total
FROM   sales_orders o
JOIN   customers    c ON c.customer_id = o.customer_id
ORDER  BY o.order_date DESC
LIMIT  5;

-- 2. Verify: every order has a customer (count of join = sales_orders count).
SELECT COUNT(*) AS joined
FROM   sales_orders o
JOIN   customers    c USING (customer_id);
-- 2,242 (same as sales_orders).

-- 3. INNER JOIN drops unmatched: customers x countries returns only 31 of 50.
SELECT COUNT(*) AS matched
FROM   customers c
JOIN   countries ctry ON ctry.country = c.country;

-- 4. LEFT JOIN to find what didn't match: 19 customers with country values
--    the countries dimension doesn't recognize (USA, us, Great Britain, ...).
SELECT c.customer_name, c.country AS raw_country
FROM   customers c
LEFT JOIN countries ctry ON ctry.country = c.country
WHERE  ctry.country IS NULL
LIMIT  10;

-- 5. The wrong-cardinality trap: revenue by category via a 3-table join.
--    Looks reasonable. Total comes back at $50M. The company didn't book $50M.
SELECT p.category,
       ROUND(SUM(CAST(o.order_total AS REAL)), 0) AS revenue_WRONG
FROM   sales_orders      o
JOIN   sales_order_lines l USING (order_id)
JOIN   products          p USING (product_id)
GROUP  BY p.category
ORDER  BY revenue_WRONG DESC;

-- 6. Proof of the bug: SUM on sales_orders alone = $11.5M (the truth).
SELECT ROUND(SUM(CAST(order_total AS REAL)), 0) AS revenue_truth
FROM   sales_orders;
-- Why was the previous query 4.3x too high?
-- sales_orders has 2,242 rows; sales_order_lines has 7,855.
-- Joining orders to lines duplicates each order by its line count
-- (~3.5 lines per order). SUM(order_total) then counts every order ~3.5x.

-- 7. The fix: aggregate at the line grain. SUM line_total from
--    sales_order_lines directly (no join through sales_orders at all).
SELECT p.category,
       ROUND(SUM(CAST(l.line_total AS REAL)), 0) AS revenue
FROM   sales_order_lines l
JOIN   products          p USING (product_id)
GROUP  BY p.category
ORDER  BY revenue DESC;
-- Same total ($11.5M), correctly distributed across categories.

-- 8. The 30-second join debug: COUNT(*) before you SUM.
SELECT COUNT(*) AS orders_only        FROM sales_orders;                                    -- 2,242
SELECT COUNT(*) AS orders_joined_lines FROM sales_orders o JOIN sales_order_lines l USING (order_id); -- 7,855
-- If join count > left count, your join is one-to-many. Don't SUM order-grain
-- columns on a line-grain query.
