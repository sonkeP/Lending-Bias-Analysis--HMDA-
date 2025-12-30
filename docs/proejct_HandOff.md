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

## 5. Project Structure
### Lending Bias Analysis (HMDA)/
## Project Directory Structure

```text
.
├── data/
│   ├── clean/                 # Gitignored (not uploaded)
│   └── analytics/             # Gitignored (not uploaded)
│
├── outputs/
│   ├── dq_logs/               # Data quality logs
│   ├── summary_tables/        # Intermediate and summary tables
│   └── final/
│       └── csv/               # Power BI–ready exports
│
├── src/
│   ├── etl/
│   │   └── build_analytics_2023.py
│   └── analysis/
│       ├── build_final_outputs.py
│       └── export_final_csvs.py
│
├── notebooks/
│   ├── 01_ingestion_cleaning.ipynb
│   ├── 02_summary_stats.ipynb
│   ├── 03_income_bucketing.ipynb
│   ├── 04_sanity_check_analytics.ipynb
│   ├── 05_loan_purpose_control.ipynb
│   └── 06_bias_analysis.ipynb
│
├── docs/
│   ├── PROJECT_HANDOFF.md
│   ├── data_dictionary.md
│   └── architecture.md
│
├── requirements.txt
├── README.md
└── .gitignore
```
- Chunked ingestion of HMDA 2023 (200k rows per chunk)
- Standardized applicant gender
- Removed unknown gender values
- Removed invalid and negative income values
- Wrote cleaned outputs as parquet partitions

## 6. Data Ingestion & Cleaning (Completed)

### Key Actions
- Chunked ingestion of HMDA 2023 (200k rows per chunk)
- Standardized applicant gender
- Removed unknown gender values
- Removed invalid and negative income values
- Wrote cleaned outputs as parquet partitions

### Outputs
- Clean parquet partitions:
  - `data/clean/hmda/hmda_2023_parts/part_*.parquet`
- Data quality log:
  - `outputs/dq_logs/dq_log_2023.csv`
- Initial summary table:
  - `outputs/summary_tables/summary_gender_2023_sample.csv`

---

## 7. Local ETL & Analytics Layer (Completed)

A reproducible local ETL pipeline builds an analytics-ready layer from cleaned data.

### Run ETL
```bash
python src/etl/build_analytics_2023.py
```
##Analytics Outputs

Generated under:

data/analytics/hmda/

- Fact table

- fact_loans_2023.parquet (one row per application)

- Dimensions

- dim_applicants.parquet

- dim_income.parquet

- dim_geography.parquet

- dim_lenders.parquet

Controlled aggregations (approval analysis)

- agg_gender_income_state.parquet

- agg_gender_income_state_purpose.parquet



## 8. Controlled Bias Measurement + Statistical Testing (Completed)


### Comparison Framework
Comparisons are conducted **within the same**:
- `state_code`
- `income_bucket`
- `loan_purpose`

This ensures outcomes are evaluated under comparable conditions and reduces confounding effects.

---

### Bias Metrics Computed

- **Approval Gap**  
approval_rate_male − approval_rate_female



- **Disparate Impact**  
approval_rate_female / approval_rate_male



---

### Sample Reliability Filter
- A **minimum number of applications per gender group** is required.
- Comparisons that do not meet this threshold are excluded to ensure statistical reliability.

---

### Statistical Significance Testing
- **Chi-square tests** are applied to:
approval outcome × gender

- Used to determine whether observed approval differences are statistically significant.

---

### Key Outputs

- **Statistically Significant Cases Table**  
Generated from the notebook and saved as:

data/analytics/hmda/gender_bias_significant_cases.parquet


This table contains only comparisons that pass both the sample reliability filter and statistical significance testing.



