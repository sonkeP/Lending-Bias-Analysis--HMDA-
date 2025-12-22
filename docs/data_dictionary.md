# HMDA 2023 – Data Dictionary (Clean Layer)

## Source
HMDA Modified Loan/Application Register (LAR), 2023 (pipe-delimited TXT).

## Tables / Files
- `data/clean/hmda/hmda_2023_parts/part_*.parquet` (clean chunked parquet)
- `data/clean/hmda/hmda_2023_sample.parquet` (sample for EDA)

## Field Definitions

| Clean Field | HMDA Raw Field | Type | Meaning | Cleaning Notes |
|---|---|---|---|---|
| activity_year | activity_year | int | Reporting year | Keep as numeric |
| lei | lei | str | Lender identifier | Used for lender-level bias flags |
| loan_type | loan_type | int | Conventional/FHA/VA/USDA | Keep as numeric code |
| loan_purpose | loan_purpose | int | Home purchase/refi/etc. | Keep as numeric code |
| occupancy_type | occupancy_type | int | Primary/secondary/investment | Keep as numeric code |
| loan_amount | loan_amount | float | Loan amount (HMDA units) | Coerced to numeric; nulls removed |
| interest_rate | interest_rate | float | Interest rate | Coerced to numeric |
| income | income | float | Applicant income (HMDA units) | Coerced to numeric; nulls removed |
| action_taken | action_taken | int | Loan outcome | Codes used to define approval |
| approved | derived | int (0/1) | Approved flag | 1 if action_taken in {1,2} else 0 |
| applicant_sex | applicant_sex | int | Applicant sex code | 1=Male, 2=Female, else Unknown |
| co_applicant_sex | co_applicant_sex | int | Co-applicant sex code | Same mapping as applicant |
| applicant_gender | derived | category | Male/Female/Unknown | Mapped from applicant_sex |
| co_applicant_gender | derived | category | Male/Female/Unknown | Mapped from co_applicant_sex |
| state_code | state_code | str | State | Required (nulls removed) |
| county_code | county_code | str | County code | Used for county-level analysis |
| census_tract | census_tract | str | Census tract | Used for tract-level hotspots |
| denial_reason_1..4 | denial_reason_1..4 | int | Denial reasons | Kept for denial pattern analysis |

## Filters Applied in Clean Layer
- Removed rows with null `loan_amount`, `income`, or `state_code`
- Parsed file in chunks (200k rows) and wrote clean parquet parts
- Skipped malformed lines during parsing (`on_bad_lines="skip"`)
