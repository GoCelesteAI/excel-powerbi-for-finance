#!/bin/bash
# Builds atlasparts.db from the 9 CSVs. Re-runs cleanly: drops + recreates.
# Used by the SQL for Finance series. Output: atlasparts.db at this directory.

set -e
cd "$(dirname "$0")"

DB="atlasparts.db"
rm -f "$DB"

sqlite3 "$DB" <<'SQL'
.mode csv
.import data/chart_of_accounts.csv chart_of_accounts
.import data/countries.csv countries
.import data/customers.csv customers
.import data/vendors.csv vendors
.import data/products.csv products
.import data/sales_orders.csv sales_orders
.import data/sales_order_lines.csv sales_order_lines
.import data/ap_invoices.csv ap_invoices
.import data/gl_journal.csv gl_journal
SQL

# After CSV import, columns are TEXT. We don't recast in this loader — episodes
# show CAST(... AS REAL) and CAST(... AS INTEGER) explicitly so viewers see the
# typing layer of SQLite. If a future episode needs a typed schema, add a
# build-db-typed.sh sibling rather than mutating this one.

echo "Built $DB:"
sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
echo ""
echo "Row counts:"
sqlite3 "$DB" <<'SQL'
.headers on
.mode column
SELECT 'chart_of_accounts' AS table_name, COUNT(*) AS rows FROM chart_of_accounts
UNION ALL SELECT 'countries',         COUNT(*) FROM countries
UNION ALL SELECT 'customers',         COUNT(*) FROM customers
UNION ALL SELECT 'vendors',           COUNT(*) FROM vendors
UNION ALL SELECT 'products',          COUNT(*) FROM products
UNION ALL SELECT 'sales_orders',      COUNT(*) FROM sales_orders
UNION ALL SELECT 'sales_order_lines', COUNT(*) FROM sales_order_lines
UNION ALL SELECT 'ap_invoices',       COUNT(*) FROM ap_invoices
UNION ALL SELECT 'gl_journal',        COUNT(*) FROM gl_journal;
SQL
