# Team review rules (test fixture)

## PY-NAME-01: Python functions use snake_case
Applies to: Python; `src/**/*.py`, `tests/**/*.py`. Exception: names required by an external protocol may retain its exact spelling.

## PY-LOG-02: Use structured logging, not print
Applies to: Python production code under `src/**`. Do not log personal data or secrets. Tests and command-line examples may use print.

## PY-SQL-03: Bind all values in SQL queries
Applies to: Python database access. Use placeholders and bound parameters; never interpolate untrusted values into SQL.

## PY-TIME-04: Store cross-region event time as aware UTC
Applies to: Python production event timestamps. Use timezone-aware UTC values.

## PY-API-05: Validate external request fields strictly
Applies to: Python API request models. Reject unknown fields unless the endpoint explicitly documents forward-compatible passthrough.

## PY-ERR-06: Translate only expected exceptions
Applies to: Python library/service code. Do not catch broad Exception where a specific error can be handled.

## PY-CURRENCY-07: Round monetary totals at the documented boundary
Applies to: Python checkout service. Quantize payable totals to two decimal places using the documented rounding mode.

## PY-PAGE-08: Public pagination is one-based
Applies to: Python API pagination helpers. Convert page to zero-based offset before slicing.

## PY-IMPORT-09: Keep imports consistent with exported symbols
Applies to: Python modules. Renamed exports require updating all import sites.

## PY-PRIV-10: Do not put personal identifiers in routine logs
Applies to: Python production logs. Use aggregate or opaque identifiers only when operationally necessary.
