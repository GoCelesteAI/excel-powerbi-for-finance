# AtlasParts Corp — Shared Dataset Spec

Single fictional company used across all 12 episodes of the Excel & Power BI for Finance series. Every formula example, pivot, model, and dashboard pulls from this one dataset so viewers build mental continuity over the whole series.

## The company

**AtlasParts Corp** — regional B2B distributor of automotive parts. Sells to auto repair shops, fleet operators, retail chains, and other wholesalers across US, Canada, UK, Germany, and France. ~$10M annual revenue, ~5% net margin, FY 2025 (Jan 1 – Dec 31, 2025).

The vertical is chosen deliberately:
- Distribution = clean buy/sell flow → straightforward COGS, AR, AP, inventory
- Auto parts = tangible, intuitive products (most viewers know what a brake pad is)
- Mid-size = realistic data volume, not toy
- Multi-country = sets up Power BI multi-currency / region slicing in S2

## Files (CSV, in `data/`)

| File | Rows | Purpose |
|------|------|---------|
| `chart_of_accounts.csv` | 70 | GL account hierarchy (5 types, 3-level parent). Used Ep1, Ep2, Ep3 (lookups). |
| `customers.csv` | 50 | Customer master. **Intentionally messy** — country codes inconsistent (US/U.S./USA/United States…), trailing whitespace in some names. Used Ep5 (Power Query cleanup). |
| `vendors.csv` | 30 | Vendor master. Lightly messy (mixed casing). |
| `products.csv` | 100 | SKU master with categories (Brakes/Engine/Electrical/Suspension/Body/Accessories). A few rows with empty `category` for cleanup demos. |
| `sales_orders.csv` | ~2,200 | SO headers (FY 2025, Q4-weighted). Mix of Closed / Shipped / Open status. |
| `sales_order_lines.csv` | ~7,800 | SO line items. Used for revenue/margin pivots. |
| `ap_invoices.csv` | 420 | Vendor invoices. Mix of Paid/Open. Most feed inventory replenishment, some opex. |
| `gl_journal.csv` | ~22,000 | The headline file. Double-entry GL postings derived from all transactions + monthly accruals + payroll + depreciation + opening balances. |

Total: ~30K rows. Excel handles this comfortably; Power BI laughs at it.

## Realism rules

- **Trial balance balances.** Sum of debits = sum of credits across the year. Verified by the generator.
- **Foreign keys are consistent.** Every customer_id in sales_orders exists in customers.csv. Same for vendors, products, accounts.
- **Q4 is heavier.** Nov is the peak month (~$1.5M revenue), seasonal pattern realistic for auto parts. Lowest months: Jan/Feb (~$500-600K each).
- **Opening balances** are seeded into a `JE-OPEN-2025` journal entry on 2025-01-01 (Cash, Inventory, AR, AP, Equity) so episodes can teach trial balance from a real starting point.
- **Monthly recurring entries:** payroll (last business day), rent (1st), utilities (5th), depreciation (last day), insurance (15th).
- **Intentional messiness — masters only, never in GL:**
  - Country codes: mix of "US", "U.S.", "USA", "United States" — Ep5 Power Query cleans this
  - Trailing/leading whitespace in some customer/vendor names
  - A few products with empty `category` field
  - Inconsistent casing in some vendor names
- The GL itself stays clean — it's the system of record.

## Reproducibility

Generator uses a fixed random seed (`SEED = 26`). Re-running `python3 generate.py` produces byte-identical CSVs. This matters because:
- Episode narrations reference specific numbers ("AtlasParts shipped $2.3M in October")
- Quizzes reference specific values
- Viewers downloading the files get the same data the video shows

If the dataset ever needs adjustment, bump the seed and re-record affected episodes deliberately — don't drift silently.

## Generation

```
cd lessons/excel-powerbi/atlasparts
python3 generate.py
```

Outputs all CSVs to `data/`. Stdlib only — no external dependencies. XLSX export for codegiz downloadables can be added later via `openpyxl` when the platform integration is built.
