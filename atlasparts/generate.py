#!/usr/bin/env python3
"""AtlasParts Corp dataset generator.

Stdlib only. Fixed seed for byte-identical reproducibility across runs.
See SPEC.md for the dataset's purpose and contract.
"""

import csv
import os
import random
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

SEED = 26
OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
FY_START = date(2025, 1, 1)
FY_END = date(2025, 12, 31)

random.seed(SEED)


# ============================================================================
# Static data — handcrafted for realism
# ============================================================================

# Chart of Accounts — (id, name, type, parent_id)
# type ∈ {Asset, Liability, Equity, Revenue, Expense}
COA_ROWS = [
  # Assets
  (1000, "Cash", "Asset", None),
  (1010, "Cash - Operating", "Asset", 1000),
  (1020, "Cash - Payroll", "Asset", 1000),
  (1100, "Accounts Receivable", "Asset", None),
  (1200, "Inventory", "Asset", None),
  (1210, "Inventory - Brakes", "Asset", 1200),
  (1220, "Inventory - Engine", "Asset", 1200),
  (1230, "Inventory - Electrical", "Asset", 1200),
  (1240, "Inventory - Suspension", "Asset", 1200),
  (1250, "Inventory - Body", "Asset", 1200),
  (1260, "Inventory - Accessories", "Asset", 1200),
  (1300, "Prepaid Expenses", "Asset", None),
  (1310, "Prepaid Insurance", "Asset", 1300),
  (1320, "Prepaid Rent", "Asset", 1300),
  (1500, "Property, Plant & Equipment", "Asset", None),
  (1510, "Equipment", "Asset", 1500),
  (1520, "Vehicles", "Asset", 1500),
  (1530, "Buildings", "Asset", 1500),
  (1600, "Accumulated Depreciation", "Asset", None),
  (1610, "Accum Depreciation - Equipment", "Asset", 1600),
  (1620, "Accum Depreciation - Vehicles", "Asset", 1600),
  (1630, "Accum Depreciation - Buildings", "Asset", 1600),
  # Liabilities
  (2000, "Accounts Payable", "Liability", None),
  (2100, "Accrued Liabilities", "Liability", None),
  (2110, "Accrued Wages", "Liability", 2100),
  (2120, "Accrued Expenses", "Liability", 2100),
  (2200, "Sales Tax Payable", "Liability", None),
  (2300, "Notes Payable", "Liability", None),
  (2400, "Long-Term Debt", "Liability", None),
  # Equity
  (3000, "Common Stock", "Equity", None),
  (3100, "Retained Earnings", "Equity", None),
  # Revenue
  (4000, "Product Sales", "Revenue", None),
  (4010, "Sales - Brakes", "Revenue", 4000),
  (4020, "Sales - Engine", "Revenue", 4000),
  (4030, "Sales - Electrical", "Revenue", 4000),
  (4040, "Sales - Suspension", "Revenue", 4000),
  (4050, "Sales - Body", "Revenue", 4000),
  (4060, "Sales - Accessories", "Revenue", 4000),
  (4100, "Sales Discounts", "Revenue", None),
  (4200, "Sales Returns", "Revenue", None),
  # COGS
  (5000, "Cost of Goods Sold", "Expense", None),
  (5010, "COGS - Brakes", "Expense", 5000),
  (5020, "COGS - Engine", "Expense", 5000),
  (5030, "COGS - Electrical", "Expense", 5000),
  (5040, "COGS - Suspension", "Expense", 5000),
  (5050, "COGS - Body", "Expense", 5000),
  (5060, "COGS - Accessories", "Expense", 5000),
  # Operating expenses
  (6000, "Salaries & Wages", "Expense", None),
  (6010, "Wages - Sales", "Expense", 6000),
  (6020, "Wages - Warehouse", "Expense", 6000),
  (6030, "Wages - Admin", "Expense", 6000),
  (6100, "Rent Expense", "Expense", None),
  (6200, "Utilities", "Expense", None),
  (6210, "Electricity", "Expense", 6200),
  (6220, "Internet & Phone", "Expense", 6200),
  (6300, "Marketing & Advertising", "Expense", None),
  (6400, "Insurance Expense", "Expense", None),
  (6500, "Office Supplies", "Expense", None),
  (6600, "Travel & Entertainment", "Expense", None),
  (6700, "Depreciation Expense", "Expense", None),
  (6710, "Depreciation - Equipment", "Expense", 6700),
  (6720, "Depreciation - Vehicles", "Expense", 6700),
  (6730, "Depreciation - Buildings", "Expense", 6700),
  (6800, "Software & Subscriptions", "Expense", None),
  (6900, "Professional Services", "Expense", None),
  (7000, "Bank Fees", "Expense", None),
  (7100, "Bad Debt Expense", "Expense", None),
  # Other
  (8000, "Interest Income", "Revenue", None),
  (8100, "Interest Expense", "Expense", None),
  (9000, "Income Tax Expense", "Expense", None),
]

# Per-category mapping of inventory / COGS / revenue accounts
CATEGORY_ACCOUNTS = {
  "Brakes":      {"inventory": 1210, "cogs": 5010, "revenue": 4010},
  "Engine":      {"inventory": 1220, "cogs": 5020, "revenue": 4020},
  "Electrical":  {"inventory": 1230, "cogs": 5030, "revenue": 4030},
  "Suspension":  {"inventory": 1240, "cogs": 5040, "revenue": 4040},
  "Body":        {"inventory": 1250, "cogs": 5050, "revenue": 4050},
  "Accessories": {"inventory": 1260, "cogs": 5060, "revenue": 4060},
}

# Customer name pool — short list, expanded by suffix
CUSTOMER_BASES = [
  "Acme", "King", "Summit", "Midwest", "Pacific", "Atlantic", "Highland",
  "Riverside", "Lakeside", "Pinecrest", "Cedar", "Maple", "Oakwood", "Ironclad",
  "Stellar", "Apex", "Vanguard", "Frontier", "Continental", "Heritage",
  "Premier", "Reliable", "Express", "Velocity", "Horizon", "Cardinal",
  "Phoenix", "Granite", "Beacon", "Northstar", "Silverline", "Goldline",
  "Bluefield", "Greenfield", "Brookhaven", "Ashford", "Fairview", "Rockport",
  "Wellington", "Camden", "Brighton", "Sterling", "Cambridge", "Oxford",
  "Hamilton", "Kingston", "Bayside", "Coastal", "Westwind", "Eastgate",
]
CUSTOMER_TYPES = [
  ("Auto Repair", "Auto Repair", ["Auto Repair", "Service Center", "Garage", "Auto Care"]),
  ("Fleet", "Fleet Operator", ["Fleet Services", "Logistics", "Transport", "Delivery"]),
  ("Retail", "Retail Chain", ["Auto Parts", "Parts Plus", "Auto Supply"]),
  ("Wholesale", "Wholesale Distributor", ["Distributors", "Wholesale", "Trade"]),
]
COUNTRIES_WEIGHTED = (
  ["US"] * 30 + ["Canada"] * 5 + ["UK"] * 8 + ["Germany"] * 5 + ["France"] * 2
)
# Intentionally messy variants of country codes — for Ep5 Power Query cleanup
US_VARIANTS = ["US", "U.S.", "USA", "United States", "U.S.A.", "us", "United States of America"]
UK_VARIANTS = ["UK", "U.K.", "United Kingdom", "Great Britain", "GB"]
DE_VARIANTS = ["Germany", "DE", "Deutschland"]

VENDOR_BASES = [
  "Brembo", "Bosch", "Monroe", "Denso", "ACDelco", "Federal-Mogul", "Mahle",
  "NGK", "Valvoline", "Castrol", "Mobil", "Continental", "Michelin", "Goodyear",
  "Delphi", "Hella", "Magna", "Lear", "Aisin", "BorgWarner", "Schaeffler",
  "ZF", "Gates", "Dayco", "Champion", "Wagner", "Raybestos", "Akebono",
  "Sachs", "KYB",
]
VENDOR_SUFFIXES = ["Inc.", "Corp.", "Ltd.", "GmbH", "Industries", "Manufacturing", "Group", "Systems"]

# Product templates — (category, [name templates])
PRODUCT_TEMPLATES = {
  "Brakes": [
    "Brake Pad Set - {model}", "Brake Rotor - {model}", "Brake Caliper - {model}",
    "Brake Line - {model}", "Brake Fluid DOT4 - {size}",
  ],
  "Engine": [
    "Oil Filter - {model}", "Air Filter - {model}", "Spark Plug Set - {model}",
    "Timing Belt - {model}", "Head Gasket - {model}", "Fuel Pump - {model}",
  ],
  "Electrical": [
    "Alternator - {model}", "Starter Motor - {model}", "Battery 12V - {size}",
    "O2 Sensor - {model}", "MAF Sensor - {model}",
  ],
  "Suspension": [
    "Shock Absorber - {model}", "Strut Assembly - {model}", "Coil Spring - {model}",
    "Control Arm - {model}", "Bushing Kit - {model}",
  ],
  "Body": [
    "Front Bumper - {model}", "Side Mirror - {model}", "Headlight Assembly - {model}",
    "Wiper Blade - {size}",
  ],
  "Accessories": [
    "Floor Mat Set - {model}", "Seat Cover - {model}", "Steering Wheel Cover - {model}",
    "Cargo Liner - {model}",
  ],
}
MODEL_TAGS = ["A1", "B2", "C3", "D4", "E5", "F6", "G7", "H8", "J9", "K10",
              "L11", "M12", "N13", "P14", "Q15", "R16", "S17", "T18", "V19", "W20"]
SIZE_TAGS = ["S", "M", "L", "XL", "Std", "HD"]

PRODUCT_TARGET_BY_CATEGORY = {
  "Brakes": 20, "Engine": 22, "Electrical": 16, "Suspension": 16,
  "Body": 12, "Accessories": 14,
}  # totals 100


# ============================================================================
# Helpers
# ============================================================================

def money(x):
  """Round to 2dp using banker-friendly half-up."""
  return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def random_business_day(start, end):
  while True:
    delta = (end - start).days
    d = start + timedelta(days=random.randint(0, delta))
    if d.weekday() < 5:
      return d

def last_business_day_of_month(year, month):
  if month == 12:
    next_month = date(year + 1, 1, 1)
  else:
    next_month = date(year, month + 1, 1)
  d = next_month - timedelta(days=1)
  while d.weekday() >= 5:
    d -= timedelta(days=1)
  return d

def write_csv(filename, header, rows):
  path = os.path.join(OUT_DIR, filename)
  with open(path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(rows)
  print(f"  wrote {filename:30s} {len(rows):>5} rows")


# ============================================================================
# Master generators
# ============================================================================

def gen_chart_of_accounts():
  rows = []
  for acc_id, name, acc_type, parent in COA_ROWS:
    rows.append([acc_id, name, acc_type, parent if parent is not None else "", "Y"])
  return rows


def gen_customers():
  rows = []
  used_names = set()
  for i in range(1, 51):
    cust_id = f"CUST-{i:03d}"
    base = random.choice(CUSTOMER_BASES)
    type_short, industry, suffixes = random.choice(CUSTOMER_TYPES)
    suffix = random.choice(suffixes)
    name = f"{base} {suffix}"
    # Ensure uniqueness
    n = 2
    while name in used_names:
      name = f"{base} {suffix} {n}"
      n += 1
    used_names.add(name)

    clean_country = random.choice(COUNTRIES_WEIGHTED)
    # Region derives from the clean country before we mess up the country field
    region = {
      "US": random.choice(["Northeast", "Midwest", "South", "West"]),
      "Canada": random.choice(["Ontario", "Quebec", "British Columbia", "Alberta"]),
      "UK": random.choice(["England", "Scotland", "Wales"]),
      "Germany": random.choice(["Bavaria", "Berlin", "Hamburg", "NRW"]),
      "France": random.choice(["Île-de-France", "Provence", "Normandy"]),
    }[clean_country]

    # Inject mess into ~25% of country values (Ep5 Power Query target)
    country = clean_country
    if random.random() < 0.25:
      if clean_country == "US":
        country = random.choice(US_VARIANTS)
      elif clean_country == "UK":
        country = random.choice(UK_VARIANTS)
      elif clean_country == "Germany":
        country = random.choice(DE_VARIANTS)
    # Trailing/leading whitespace in some names (Ep5 cleanup)
    if random.random() < 0.10:
      name = name + "  "
    if random.random() < 0.05:
      name = "  " + name

    credit_limit = random.choice([10000, 25000, 50000, 75000, 100000, 150000, 250000])
    payment_terms = random.choice(["Net 30", "Net 30", "Net 30", "Net 45", "Net 60", "Due on Receipt"])
    rows.append([cust_id, name, country, region, industry, credit_limit, payment_terms, "Y"])
  return rows


def gen_vendors():
  rows = []
  used = set()
  for i in range(1, 31):
    vend_id = f"VEND-{i:03d}"
    base = random.choice(VENDOR_BASES)
    suffix = random.choice(VENDOR_SUFFIXES)
    name = f"{base} {suffix}"
    while name in used:
      base = random.choice(VENDOR_BASES)
      suffix = random.choice(VENDOR_SUFFIXES)
      name = f"{base} {suffix}"
    used.add(name)

    # Mess: inconsistent casing
    if random.random() < 0.15:
      name = name.upper()
    elif random.random() < 0.10:
      name = name.lower()

    country = random.choice(["US", "US", "US", "Germany", "Japan", "UK", "Italy"])
    payment_terms = random.choice(["Net 30", "Net 45", "Net 60", "Net 60", "2/10 Net 30"])
    rows.append([vend_id, name, country, payment_terms, "Y"])
  return rows


def gen_products():
  rows = []
  pid = 10000
  for category, target in PRODUCT_TARGET_BY_CATEGORY.items():
    templates = PRODUCT_TEMPLATES[category]
    for _ in range(target):
      tpl = random.choice(templates)
      name = tpl.format(model=random.choice(MODEL_TAGS), size=random.choice(SIZE_TAGS))
      # Cost varies by category
      base_cost = {
        "Brakes": (40, 220), "Engine": (15, 380), "Electrical": (25, 450),
        "Suspension": (35, 280), "Body": (60, 520), "Accessories": (8, 90),
      }[category]
      unit_cost = money(random.uniform(*base_cost))
      list_price = money(unit_cost * random.uniform(1.32, 1.55))
      stock = random.randint(20, 800)
      sku = f"SKU-{pid:05d}"
      pid += 1
      # Mess: a few products with empty category (Ep5 cleanup)
      cat_field = category if random.random() > 0.04 else ""
      rows.append([sku, name, cat_field, unit_cost, list_price, stock])
  return rows


# ============================================================================
# Transaction generators
# ============================================================================

def month_weight(d):
  """Q4-weighted seasonal pattern. Returns relative weight 0.5–1.7."""
  m = d.month
  return {1: 0.6, 2: 0.6, 3: 0.85, 4: 0.95, 5: 0.95, 6: 0.9,
          7: 0.85, 8: 0.85, 9: 0.95, 10: 1.4, 11: 1.6, 12: 1.5}[m]


def gen_sales_orders(customers, products):
  orders = []
  lines = []
  order_seq = 1
  line_seq = 1
  cust_ids = [c[0] for c in customers]

  # Generate ~2200 orders/year, weighted by month — sized for ~$10M annual revenue
  for month in range(1, 13):
    n_orders = int(random.uniform(150, 220) * month_weight(date(2025, month, 15)))
    for _ in range(n_orders):
      d = random_business_day(date(2025, month, 1),
                              date(2025, month, 28) if month == 2
                              else date(2025, month, 30 if month in (4, 6, 9, 11) else 31))
      cust_id = random.choice(cust_ids)
      order_id = f"SO-{order_seq:05d}"
      order_seq += 1

      # 1-6 lines per order
      n_lines = random.randint(1, 6)
      order_total = 0.0
      chosen = random.sample(products, min(n_lines, len(products)))
      for p in chosen:
        sku, pname, pcat, pcost, pprice, pstock = p
        qty = random.choice([1, 1, 2, 2, 3, 4, 5, 8, 10, 12, 20])
        # Occasional discount
        unit_price = pprice * (1.0 - random.choice([0, 0, 0, 0.05, 0.08, 0.10]))
        unit_price = money(unit_price)
        line_total = money(unit_price * qty)
        order_total += line_total
        lines.append([
          f"L-{line_seq:06d}", order_id, sku, qty, unit_price, line_total
        ])
        line_seq += 1

      # Status: most shipped, some open near year-end
      if d > date(2025, 12, 15):
        status = random.choices(["Shipped", "Open"], weights=[0.4, 0.6])[0]
      else:
        status = random.choices(["Shipped", "Closed", "Open"], weights=[0.55, 0.4, 0.05])[0]

      orders.append([order_id, d.isoformat(), cust_id, status, "USD", money(order_total)])

  return orders, lines


def gen_ap_invoices(vendors):
  rows = []
  vend_ids = [v[0] for v in vendors]
  for i in range(1, 421):
    inv_id = f"INV-{i:05d}"
    vendor_id = random.choice(vend_ids)
    d = random_business_day(FY_START, FY_END)
    due_date = d + timedelta(days=random.choice([30, 30, 45, 60]))
    amount = money(random.uniform(500, 28000))
    # Most paid, recent ones still open
    if d > date(2025, 11, 1):
      status = random.choices(["Paid", "Open"], weights=[0.4, 0.6])[0]
    else:
      status = random.choices(["Paid", "Open"], weights=[0.92, 0.08])[0]
    rows.append([inv_id, vendor_id, d.isoformat(), due_date.isoformat(), amount, status])
  return rows


# ============================================================================
# GL derivation — every transaction produces double-entry postings
# ============================================================================

def derive_gl(coa, products, customers, sales_orders, sales_lines, ap_invoices):
  """Produce GL journal lines. Returns list of rows.

  Schema: journal_id, line_id, posting_date, account_id, debit, credit,
          description, source_doc, cost_center
  """
  gl = []
  jid_seq = 1
  lid_seq = 1

  def add(date_, account, debit, credit, desc, source, cost_center=""):
    nonlocal lid_seq
    gl.append([
      f"JE-{jid_seq:06d}",
      f"GL-{lid_seq:06d}",
      date_.isoformat(),
      account,
      money(debit),
      money(credit),
      desc,
      source,
      cost_center,
    ])
    lid_seq += 1

  def new_je():
    nonlocal jid_seq
    jid_seq += 1

  product_lookup = {p[0]: p for p in products}  # sku -> row

  # ----- Opening balances on 2025-01-01 -----
  opening = [
    (1010, 850000.00, 0.00, "Opening Cash - Operating"),
    (1020, 75000.00, 0.00, "Opening Cash - Payroll"),
    (1100, 1250000.00, 0.00, "Opening Accounts Receivable"),
    (1210, 480000.00, 0.00, "Opening Inventory - Brakes"),
    (1220, 620000.00, 0.00, "Opening Inventory - Engine"),
    (1230, 410000.00, 0.00, "Opening Inventory - Electrical"),
    (1240, 350000.00, 0.00, "Opening Inventory - Suspension"),
    (1250, 280000.00, 0.00, "Opening Inventory - Body"),
    (1260, 180000.00, 0.00, "Opening Inventory - Accessories"),
    (1320, 60000.00, 0.00, "Opening Prepaid Rent"),
    (1310, 36000.00, 0.00, "Opening Prepaid Insurance"),
    (1510, 480000.00, 0.00, "Opening Equipment"),
    (1520, 320000.00, 0.00, "Opening Vehicles"),
    (1530, 1800000.00, 0.00, "Opening Buildings"),
    (1610, 0.00, 192000.00, "Opening Accum Depr - Equipment"),
    (1620, 0.00, 96000.00, "Opening Accum Depr - Vehicles"),
    (1630, 0.00, 540000.00, "Opening Accum Depr - Buildings"),
    (2000, 0.00, 685000.00, "Opening Accounts Payable"),
    (2110, 0.00, 42000.00, "Opening Accrued Wages"),
    (2300, 0.00, 350000.00, "Opening Notes Payable"),
    (2400, 0.00, 1200000.00, "Opening Long-Term Debt"),
    (3000, 0.00, 1000000.00, "Opening Common Stock"),
  ]
  total_d = sum(d for _, d, _, _ in opening)
  total_c = sum(c for _, _, c, _ in opening)
  # Balance the rest into Retained Earnings
  re_balance = total_d - total_c
  opening.append((3100, 0.00, re_balance, "Opening Retained Earnings"))

  for acc, d_, c_, desc in opening:
    add(FY_START, acc, d_, c_, desc, "JE-OPEN-2025")
  new_je()

  # ----- Sales orders → revenue + COGS -----
  shipped_orders = {o[0]: o for o in sales_orders if o[3] in ("Shipped", "Closed")}
  lines_by_order = defaultdict(list)
  for ln in sales_lines:
    lines_by_order[ln[1]].append(ln)

  # Track AR collected later (per customer balance pool)
  ar_balance = {}  # order_id -> outstanding amount

  for order in sales_orders:
    order_id, order_date, cust_id, status, currency, total = order
    if status == "Open":
      continue  # Open orders not yet billed
    d = date.fromisoformat(order_date)

    # Group lines by category to consolidate revenue/cogs/inventory hits
    by_cat = defaultdict(lambda: {"rev": 0.0, "cogs": 0.0})
    for ln in lines_by_order[order_id]:
      _, _, sku, qty, unit_price, line_total = ln
      product = product_lookup[sku]
      pcat = product[2] or "Accessories"  # empty category falls back
      pcat = pcat if pcat in CATEGORY_ACCOUNTS else "Accessories"
      by_cat[pcat]["rev"] += line_total
      by_cat[pcat]["cogs"] += money(product[3] * qty)

    # AR / Revenue
    add(d, 1100, total, 0, f"Invoice {order_id} to {cust_id}", order_id)
    for cat, vals in by_cat.items():
      acc = CATEGORY_ACCOUNTS[cat]["revenue"]
      add(d, acc, 0, vals["rev"], f"Sales {cat} - {order_id}", order_id)
    new_je()

    # COGS / Inventory
    for cat, vals in by_cat.items():
      cogs_acc = CATEGORY_ACCOUNTS[cat]["cogs"]
      inv_acc = CATEGORY_ACCOUNTS[cat]["inventory"]
      add(d, cogs_acc, vals["cogs"], 0, f"COGS {cat} - {order_id}", order_id)
      add(d, inv_acc, 0, vals["cogs"], f"Inventory release {cat} - {order_id}", order_id)
    new_je()

    if status == "Closed":
      # Customer paid. Pick a date 25-50 days later, capped at FY end
      pay_date = min(d + timedelta(days=random.randint(25, 50)), FY_END)
      add(pay_date, 1010, total, 0, f"Customer payment {cust_id}", order_id)
      add(pay_date, 1100, 0, total, f"Apply receipt {order_id}", order_id)
      new_je()
    else:
      ar_balance[order_id] = total

  # ----- AP invoices → expense + AP -----
  for inv in ap_invoices:
    inv_id, vendor_id, inv_date_s, due_date_s, amount, status = inv
    d = date.fromisoformat(inv_date_s)
    # Pick an expense category — most go to inventory replenishment, some opex
    # Most AP feeds inventory replenishment; small fraction goes to opex categories
    expense_acc = random.choices(
      [1210, 1220, 1230, 1240, 1250, 1260, 6500, 6600, 6800, 6900, 6300],
      weights=[18, 22, 14, 14, 10, 10, 2, 2, 2, 3, 3]
    )[0]
    add(d, expense_acc, amount, 0, f"Vendor invoice {inv_id} from {vendor_id}", inv_id)
    add(d, 2000, 0, amount, f"AP {vendor_id} - {inv_id}", inv_id)
    new_je()
    if status == "Paid":
      pay_date = min(d + timedelta(days=random.randint(20, 55)), FY_END)
      add(pay_date, 2000, amount, 0, f"AP payment {inv_id}", inv_id)
      add(pay_date, 1010, 0, amount, f"Cash payment {vendor_id}", inv_id)
      new_je()

  # ----- Monthly recurring entries -----
  for month in range(1, 13):
    # Rent — 1st of month
    rent_d = date(2025, month, 1)
    rent_amt = 12500.00
    add(rent_d, 6100, rent_amt, 0, "Monthly rent", f"REC-RENT-{month:02d}")
    add(rent_d, 1010, 0, rent_amt, "Rent payment", f"REC-RENT-{month:02d}")
    new_je()

    # Utilities — 5th
    util_d = date(2025, month, 5)
    elec = money(random.uniform(2800, 4200))
    phone = money(random.uniform(800, 1100))
    add(util_d, 6210, elec, 0, "Electricity", f"REC-UTIL-{month:02d}")
    add(util_d, 6220, phone, 0, "Internet & Phone", f"REC-UTIL-{month:02d}")
    add(util_d, 1010, 0, elec + phone, "Utility payments", f"REC-UTIL-{month:02d}")
    new_je()

    # Insurance amortization — 15th
    ins_d = date(2025, month, 15)
    ins_amt = 3000.00
    add(ins_d, 6400, ins_amt, 0, "Insurance amortization", f"REC-INS-{month:02d}")
    add(ins_d, 1310, 0, ins_amt, "Reduce prepaid insurance", f"REC-INS-{month:02d}")
    new_je()

    # Payroll — last business day. Right-sized for ~10 employees / regional distributor.
    pay_d = last_business_day_of_month(2025, month)
    sales_wage = money(random.uniform(28000, 36000))
    wh_wage = money(random.uniform(36000, 46000))
    admin_wage = money(random.uniform(22000, 30000))
    total_wage = sales_wage + wh_wage + admin_wage
    add(pay_d, 6010, sales_wage, 0, "Sales wages", f"REC-PAY-{month:02d}")
    add(pay_d, 6020, wh_wage, 0, "Warehouse wages", f"REC-PAY-{month:02d}")
    add(pay_d, 6030, admin_wage, 0, "Admin wages", f"REC-PAY-{month:02d}")
    add(pay_d, 1020, 0, total_wage, "Payroll cash out", f"REC-PAY-{month:02d}")
    new_je()

    # Depreciation — last day
    dep_d = last_business_day_of_month(2025, month)
    dep_eq = 4000.00
    dep_veh = 2667.00
    dep_bld = 4500.00
    add(dep_d, 6710, dep_eq, 0, "Depreciation - Equipment", f"REC-DEP-{month:02d}")
    add(dep_d, 1610, 0, dep_eq, "Accum depr - Equipment", f"REC-DEP-{month:02d}")
    add(dep_d, 6720, dep_veh, 0, "Depreciation - Vehicles", f"REC-DEP-{month:02d}")
    add(dep_d, 1620, 0, dep_veh, "Accum depr - Vehicles", f"REC-DEP-{month:02d}")
    add(dep_d, 6730, dep_bld, 0, "Depreciation - Buildings", f"REC-DEP-{month:02d}")
    add(dep_d, 1630, 0, dep_bld, "Accum depr - Buildings", f"REC-DEP-{month:02d}")
    new_je()

    # Marketing - mid-month
    mkt_d = date(2025, month, 10)
    mkt_amt = money(random.uniform(3500, 8500))
    add(mkt_d, 6300, mkt_amt, 0, "Marketing campaign", f"REC-MKT-{month:02d}")
    add(mkt_d, 1010, 0, mkt_amt, "Marketing payment", f"REC-MKT-{month:02d}")
    new_je()

    # Interest expense - last day on long-term debt
    int_d = last_business_day_of_month(2025, month)
    int_amt = 5000.00
    add(int_d, 8100, int_amt, 0, "Interest on long-term debt", f"REC-INT-{month:02d}")
    add(int_d, 1010, 0, int_amt, "Interest payment", f"REC-INT-{month:02d}")
    new_je()

  return gl


# ============================================================================
# Verification
# ============================================================================

def verify_trial_balance(gl_lines):
  total_debit = sum(row[4] for row in gl_lines)
  total_credit = sum(row[5] for row in gl_lines)
  diff = round(total_debit - total_credit, 2)
  print(f"\nTrial balance check:")
  print(f"  total debits:  {total_debit:>14,.2f}")
  print(f"  total credits: {total_credit:>14,.2f}")
  print(f"  difference:    {diff:>14,.2f}")
  if abs(diff) > 0.01:
    raise AssertionError(f"Trial balance does not balance: diff = {diff}")
  print("  ✓ balanced")


def verify_referential_integrity(customers, vendors, products, sales_orders,
                                  sales_lines, ap_invoices, gl_lines, coa):
  cust_ids = {c[0] for c in customers}
  vend_ids = {v[0] for v in vendors}
  sku_ids = {p[0] for p in products}
  acc_ids = {row[0] for row in coa}
  order_ids = {o[0] for o in sales_orders}

  errors = []
  for o in sales_orders:
    if o[2] not in cust_ids:
      errors.append(f"SO {o[0]} references missing customer {o[2]}")
  for ln in sales_lines:
    if ln[1] not in order_ids:
      errors.append(f"SO line {ln[0]} references missing order {ln[1]}")
    if ln[2] not in sku_ids:
      errors.append(f"SO line {ln[0]} references missing product {ln[2]}")
  for inv in ap_invoices:
    if inv[1] not in vend_ids:
      errors.append(f"AP invoice {inv[0]} references missing vendor {inv[1]}")
  for gl in gl_lines:
    if gl[3] not in acc_ids:
      errors.append(f"GL line {gl[1]} references missing account {gl[3]}")

  print(f"\nReferential integrity check:")
  if errors:
    for e in errors[:10]:
      print(f"  ✗ {e}")
    raise AssertionError(f"{len(errors)} FK violations")
  print(f"  ✓ all FKs valid")


# ============================================================================
# Main
# ============================================================================

def main():
  os.makedirs(OUT_DIR, exist_ok=True)
  print("Generating AtlasParts Corp dataset (seed=%d)..." % SEED)

  coa = gen_chart_of_accounts()
  customers = gen_customers()
  vendors = gen_vendors()
  products = gen_products()
  sales_orders, sales_lines = gen_sales_orders(customers, products)
  ap_invoices = gen_ap_invoices(vendors)
  gl_lines = derive_gl(coa, products, customers, sales_orders, sales_lines, ap_invoices)

  verify_trial_balance(gl_lines)
  verify_referential_integrity(customers, vendors, products, sales_orders,
                                sales_lines, ap_invoices, gl_lines, coa)

  print("\nWriting CSVs:")
  write_csv("chart_of_accounts.csv",
            ["account_id", "account_name", "account_type", "parent_account_id", "is_active"],
            coa)
  write_csv("customers.csv",
            ["customer_id", "customer_name", "country", "region", "industry",
             "credit_limit", "payment_terms", "is_active"],
            customers)
  write_csv("vendors.csv",
            ["vendor_id", "vendor_name", "country", "payment_terms", "is_active"],
            vendors)
  write_csv("products.csv",
            ["product_id", "product_name", "category", "unit_cost", "list_price", "units_in_stock"],
            products)
  write_csv("sales_orders.csv",
            ["order_id", "order_date", "customer_id", "status", "currency", "order_total"],
            sales_orders)
  write_csv("sales_order_lines.csv",
            ["line_id", "order_id", "product_id", "quantity", "unit_price", "line_total"],
            sales_lines)
  write_csv("ap_invoices.csv",
            ["invoice_id", "vendor_id", "invoice_date", "due_date", "amount", "status"],
            ap_invoices)
  write_csv("gl_journal.csv",
            ["journal_id", "line_id", "posting_date", "account_id", "debit", "credit",
             "description", "source_doc", "cost_center"],
            gl_lines)

  print("\nDone.")


if __name__ == "__main__":
  main()
