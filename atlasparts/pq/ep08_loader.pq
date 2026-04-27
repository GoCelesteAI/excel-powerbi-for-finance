// AtlasParts loader — Power Query at Scale (Episode 8 of Excel & Power BI for Finance).
//
// This file shows the four moves from the episode in a single .pq script:
//   1. Get Data → Folder via Folder.Files(AtlasFolder)
//   2. Add as New Query for each of the 8 CSVs (different shapes per file)
//   3. Merge customers ⨝ countries on the country column to add a region column
//   4. Parametrise the file path so the loader is portable
//
// To use: open Power BI Desktop. Home → Get Data → Blank query. Then open the
// Advanced Editor and paste the relevant `let ... in ...` block per query.
// Define a Text parameter named `AtlasFolder` first (Manage Parameters → New).

// ── Parameter ──
// In Power BI, define this via Manage Parameters → New Parameter.
//   Name: AtlasFolder
//   Type: Text
//   Current value: "C:\AtlasParts\"   (or your local path)


// ── Helper: load one named CSV from the AtlasFolder ──
// Saves repeating the Csv.Document boilerplate in every query.
//
// Save as a query named `loadCsv`:
let
  loadCsv = (fileName as text) =>
    let
      raw      = Csv.Document(File.Contents(AtlasFolder & fileName), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
      promoted = Table.PromoteHeaders(raw, [PromoteAllScalars=true])
    in
      promoted
in
  loadCsv


// ── customers (merged with countries to attach region) ──
// Save as a query named `customers`.
let
  Source = loadCsv("customers.csv"),

  // Same Season-1-Ep5 cleanup
  Typed = Table.TransformColumnTypes(Source, {
    {"customer_id", type text},
    {"customer_name", type text},
    {"country", type text},
    {"region", type text},
    {"industry", type text},
    {"credit_limit", Int64.Type},
    {"payment_terms", type text},
    {"is_active", type text}
  }),
  Trimmed = Table.TransformColumns(Typed, {
    {"customer_name", Text.Trim, type text},
    {"country", Text.Trim, type text}
  }),
  CountryUpper = Table.TransformColumns(Trimmed, {{"country", Text.Upper, type text}}),

  // Canonicalise common variants before the merge
  C1 = Table.ReplaceValue(CountryUpper, "USA", "US", Replacer.ReplaceText, {"country"}),
  C2 = Table.ReplaceValue(C1, "UNITED STATES OF AMERICA", "US", Replacer.ReplaceText, {"country"}),
  C3 = Table.ReplaceValue(C2, "GREAT BRITAIN", "UK", Replacer.ReplaceText, {"country"}),
  C4 = Table.ReplaceValue(C3, "DEUTSCHLAND", "DE", Replacer.ReplaceText, {"country"}),

  // Drop the source-side region column; we'll get it from the merge
  WithoutRegion = Table.RemoveColumns(C4, {"region"}),

  // Merge with countries (loaded as a separate query — see countries below)
  Merged = Table.NestedJoin(WithoutRegion, {"country"}, countries, {"country"}, "country_match", JoinKind.LeftOuter),
  ExpandedRegion = Table.ExpandTableColumn(Merged, "country_match", {"region"}, {"region"})
in
  ExpandedRegion


// ── countries (connection-only — used by the merge above) ──
// Save as a query named `countries`. Right-click → Enable Load → uncheck.
let
  Source = loadCsv("countries.csv"),
  Typed = Table.TransformColumnTypes(Source, {
    {"country", type text},
    {"country_name", type text},
    {"region", type text}
  }),
  CountryUpper = Table.TransformColumns(Typed, {{"country", Text.Upper, type text}})
in
  CountryUpper


// ── gl_journal (the big one — 4.1M rows) ──
// Save as a query named `gl_journal`. This is the fact-table-to-be.
let
  Source = loadCsv("gl_journal.csv"),
  Typed = Table.TransformColumnTypes(Source, {
    {"journal_id", type text},
    {"posting_date", type date},
    {"posting_period", type text},
    {"company_code", type text},
    {"account_code", type text},
    {"customer_id", type text},
    {"vendor_id", type text},
    {"product_id", type text},
    {"description", type text},
    {"debit_amount", type number},
    {"credit_amount", type number},
    {"currency", type text}
  }),
  // Replace any errors in the numeric amount columns with null
  CleanDebit = Table.ReplaceErrorValues(Typed, {{"debit_amount", null}, {"credit_amount", null}})
in
  CleanDebit


// ── chart_of_accounts ──
// Save as a query named `chart_of_accounts`. Already clean — just type.
let
  Source = loadCsv("chart_of_accounts.csv"),
  Typed = Table.TransformColumnTypes(Source, {
    {"account_code", type text},
    {"account_name", type text},
    {"account_type", type text},
    {"parent_account", type text}
  })
in
  Typed


// ── Append example (commented out — for monthly GL files if you ever have them) ──
// Save as a query named `gl_journal_full` if you split files by month.
//
// let
//   jan = loadCsv("gl_journal_2024_01.csv"),
//   feb = loadCsv("gl_journal_2024_02.csv"),
//   mar = loadCsv("gl_journal_2024_03.csv"),
//   ... twelve months ...
//   AllMonths = Table.Combine({jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec})
// in
//   AllMonths


// ── try / otherwise example for stubborn columns ──
// If amount has stray text like "(1,234.56)" mixed in, wrap the conversion:
//
//   = Table.AddColumn(Source, "amount_clean",
//       each try Number.From([amount]) otherwise null,
//       type nullable number)
//
// Push this kind of cleanup to Power Query so visuals and DAX never see errors.
