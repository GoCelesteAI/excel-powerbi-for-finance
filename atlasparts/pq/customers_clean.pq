// AtlasParts customer master cleanup recipe.
// Episode 5 of Excel & Power BI for Finance.
//
// Paste this into Power Query → Home → Advanced Editor.
// Adjust the file path on line 6 to point at your local copy of customers.csv.

let
  Source = Csv.Document(File.Contents("C:\path\to\customers.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
  PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

  // Initial type inference (will be re-asserted at the end)
  ChangedType = Table.TransformColumnTypes(PromotedHeaders, {
    {"customer_id", type text},
    {"customer_name", type text},
    {"country", type text},
    {"region", type text},
    {"industry", type text},
    {"credit_limit", Int64.Type},
    {"payment_terms", type text},
    {"is_active", type text}
  }),

  // 1. Trim whitespace on the two messy text columns
  TrimmedText = Table.TransformColumns(ChangedType, {
    {"customer_name", Text.Trim, type text},
    {"country", Text.Trim, type text}
  }),

  // 2. Uppercase country to make matching case-insensitive
  UppercasedCountry = Table.TransformColumns(TrimmedText, {
    {"country", Text.Upper, type text}
  }),

  // 3. Canonicalise US variants
  ReplacedUSA = Table.ReplaceValue(UppercasedCountry, "USA", "US", Replacer.ReplaceText, {"country"}),
  ReplacedUSofA = Table.ReplaceValue(ReplacedUSA, "UNITED STATES OF AMERICA", "US", Replacer.ReplaceText, {"country"}),

  // 4. Canonicalise UK and Germany
  ReplacedGB = Table.ReplaceValue(ReplacedUSofA, "GREAT BRITAIN", "UK", Replacer.ReplaceText, {"country"}),
  ReplacedDE = Table.ReplaceValue(ReplacedGB, "DE", "GERMANY", Replacer.ReplaceText, {"country"}),

  // 5. Title-case everything, then patch US/UK back to upper (since "Us"/"Uk" reads wrong)
  TitleCased = Table.TransformColumns(ReplacedDE, {
    {"country", Text.Proper, type text}
  }),
  PatchedUS = Table.ReplaceValue(TitleCased, "Us", "US", Replacer.ReplaceText, {"country"}),
  PatchedUK = Table.ReplaceValue(PatchedUS, "Uk", "UK", Replacer.ReplaceText, {"country"}),

  // 6. Re-assert column types now that values are clean
  ChangedColumnTypes = Table.TransformColumnTypes(PatchedUK, {
    {"customer_id", type text},
    {"customer_name", type text},
    {"country", type text},
    {"region", type text},
    {"industry", type text},
    {"credit_limit", Int64.Type},
    {"payment_terms", type text},
    {"is_active", type text}
  })
in
  ChangedColumnTypes
