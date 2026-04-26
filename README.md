# Excel & Power BI for Finance — Downloads

Companion repository for the **Excel & Power BI for Finance** YouTube series by CelesteAI. One company, one dataset, twelve episodes across two seasons.

- **Watch on YouTube:** https://www.youtube.com/playlist?list=PLOeWRYj1QznV_HcntbLKhasMm5_Z7l5i4
- **Read on codegiz:** https://codegiz.com/blog/series/excel-for-finance

## What's in this repo

```
excel-powerbi-for-finance/
├── atlasparts/                 ← the dataset, shared across all 12 episodes
│   ├── data/                   ← 8 CSV files, ~30K rows total
│   ├── generate.py             ← stdlib-only Python generator (fixed seed)
│   └── SPEC.md                 ← schema, realism rules, reproducibility notes
└── README.md
```

Per-episode workbook starters (`.xlsx`, `.pbix`) will be added under `episode01/`, `episode02/`, etc. as each episode ships.

## AtlasParts Corp

Throughout the series we work with one fictional company:

- **Regional B2B distributor of automotive parts**
- ~$10M annual revenue, ~5% net margin
- 50 customers across 5 countries (US, Canada, UK, Germany, France)
- 100 SKUs in 6 categories (Brakes, Engine, Electrical, Suspension, Body, Accessories)
- FY 2025 (Jan 1 – Dec 31, 2025)
- Trial balance verified to the cent; all foreign keys consistent

See [`atlasparts/SPEC.md`](atlasparts/SPEC.md) for full dataset documentation.

## The dataset (`atlasparts/data/`)

| File | Rows | What it is |
|------|------|------------|
| `chart_of_accounts.csv` | 70 | GL account hierarchy (assets / liabilities / equity / revenue / expenses) |
| `customers.csv` | 50 | Customer master. *Intentionally messy* — country codes inconsistent, trailing whitespace in some names. Episode 5 cleans it. |
| `vendors.csv` | 30 | Vendor master |
| `products.csv` | 100 | SKU master with categories |
| `sales_orders.csv` | ~2,200 | SO headers (Q4-weighted seasonality) |
| `sales_order_lines.csv` | ~7,800 | SO line items |
| `ap_invoices.csv` | 420 | Vendor invoices (mix of Paid / Open) |
| `gl_journal.csv` | ~22,000 | The headline file. Double-entry GL postings. |

## Reproducing the dataset

The CSVs are committed for direct download, but they're also reproducible from the generator. Stdlib-only Python — no external dependencies.

```bash
cd atlasparts
python3 generate.py
```

The generator uses a fixed random seed (`SEED = 26`), so re-running produces byte-identical CSVs. If we ever need to regenerate, we bump the seed deliberately.

## Episode index

| Ep | Title | Season |
|----|-------|--------|
| 1 | The ERP-to-Excel Pipeline | S1 — Excel for Finance |
| 2 | Reading a GL Extract | S1 |
| 3 | Lookups for Finance | S1 |
| 4 | Pivot Tables | S1 |
| 5 | Power Query in Excel | S1 |
| 6 | Robust Spreadsheets | S1 |
| 7 | From Excel to Power BI | S2 — Power BI for Finance |
| 8 | Power Query at Scale | S2 |
| 9 | Star Schema for Finance | S2 |
| 10 | DAX Fundamentals | S2 |
| 11 | Time Intelligence | S2 |
| 12 | Finance Dashboard, End-to-End | S2 |

## License

MIT — use the dataset freely for learning, teaching, blog posts, internal training, anything else.

If you build something interesting on top of it, we'd love to hear about it: open an issue or tag CelesteAI on social.
