// Joins GL journal lines to customers_clean via sales_orders.
// The Power Query equivalent of Episode 3's chained XLOOKUP — but as two
// named Merge steps instead of a nested formula.
//
// Prerequisite: customers_clean and sales_orders queries already exist
// in this workbook (built from customers_clean.pq + From Text/CSV on
// sales_orders.csv).

let
  Source = Csv.Document(File.Contents("C:\path\to\gl_journal.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

  // Step 1 — Merge gl_journal with sales_orders on source_doc to pick up customer_id
  MergedSO = Table.NestedJoin(PromotedHeaders, {"source_doc"}, sales_orders, {"order_number"}, "so", JoinKind.LeftOuter),
  ExpandedSO = Table.ExpandTableColumn(MergedSO, "so", {"customer_id"}, {"customer_id"}),

  // Step 2 — Merge result with customers_clean on customer_id to pick up country
  MergedCust = Table.NestedJoin(ExpandedSO, {"customer_id"}, customers_clean, {"customer_id"}, "cust", JoinKind.LeftOuter),
  ExpandedCust = Table.ExpandTableColumn(MergedCust, "cust", {"country"}, {"customer_country"}),

  // Re-assert types
  ChangedTypes = Table.TransformColumnTypes(ExpandedCust, {
    {"journal_id", type text},
    {"posting_date", type date},
    {"account_id", Int64.Type},
    {"debit", Currency.Type},
    {"credit", Currency.Type},
    {"customer_id", type text},
    {"customer_country", type text}
  })
in
  ChangedTypes
