# PROJECT HANDOFF
## Gender Discrimination in Credit Access — HMDA Lending Bias Analysis

---

## 1. Project Purpose

This project investigates whether mortgage lending outcomes in the United States
differ by applicant gender, and whether any observed differences persist after
controlling for income, geography, and loan characteristics.

The analysis is **observational**, not causal.  
Gender is treated as an observed attribute, not an assumed source of bias.

---

## 2. Core Research Question

> When applicants have comparable income levels, geographic location,
> and loan characteristics, do mortgage approval rates or loan amounts
> differ by gender?

---

## 3. Data Sources

### HMDA (Primary Dataset)
- Home Mortgage Disclosure Act (HMDA) Modified Loan/Application Register
- Year: **2023**
- Format: pipe-delimited text (~2.5GB)
- Key fields used:
  - applicant_gender
  - income
  - loan_amount
  - interest_rate
  - loan_purpose
  - loan_type
  - action_taken (approval outcome)
  - lender identifier (LEI)
  - geography (state, county, census tract)

### Census (Planned / Staged)
- American Community Survey (ACS) 5-Year Estimates
- Table: **B19013** — Median Household Income
- Geography: Census Tract
- Purpose: socioeconomic context (future enrichment step)

---

## 4. Environment & Tooling

- OS: Windows
- IDE: VS Code
- Python environment: `venv`
- Libraries:
  - pandas
  - pyarrow
  - duckdb
- Workflow: **local-first**, cloud-ready by design

---

## 5. Week 1 — Data Ingestion & Cleaning (Completed)

### Key Actions
- Chunked ingestion of HMDA 2023 (200k rows per chunk)
- Standardized applicant gender
- Removed unknown gender values
- Removed invalid and negative income values
- Wrote cleaned outputs as parquet partitions

### Outputs
- Clean parquet partitions:
