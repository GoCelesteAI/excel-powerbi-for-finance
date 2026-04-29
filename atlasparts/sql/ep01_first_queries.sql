-- SQL for Finance — Episode 1: Why SQL when you have Excel?
-- =====================================================================
-- The four queries shown in the episode. Run from inside the sqlite3
-- shell against atlasparts.db, or via:  sqlite3 atlasparts.db < ep01_first_queries.sql

.headers on
.mode column

-- 1. Your first SELECT — five rows from the customers table
SELECT * FROM customers LIMIT 5;

-- 2. Filter by country
SELECT customer_name, country, region
FROM   customers
WHERE  country = 'US'
LIMIT  5;

-- 3. The COUNT — 22,028 GL entries in milliseconds
SELECT COUNT(*) FROM gl_journal;

-- 4. The capstone JOIN — total debits by account type
-- (This is the query you'll be writing yourself by Episode 5.)
SELECT account_type,
       ROUND(SUM(CAST(debit AS REAL)), 2) AS total_debits
FROM   gl_journal
JOIN   chart_of_accounts USING (account_id)
GROUP  BY account_type
ORDER  BY total_debits DESC;
