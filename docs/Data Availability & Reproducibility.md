📂 Data Availability & Reproducibility
Why data is not included in this repository

The HMDA (Home Mortgage Disclosure Act) dataset is very large (the 2023 Modified LAR file alone is ~2.5GB).
To keep this repository lightweight and GitHub-friendly, raw and processed data files are intentionally excluded via .gitignore.

All results in this project are fully reproducible using the steps below.

📥 Data Sources
1. HMDA Mortgage Data (Primary)

Source: CFPB / FFIEC HMDA Public Data

URL: https://ffiec.cfpb.gov/data-publication/

Dataset used:

Modified Loan/Application Register (LAR)

Year: 2023

Format: pipe-delimited .txt

2. Census Data (Planned / Optional Enrichment)

Source: U.S. Census Bureau (ACS 5-Year)

URL: https://data.census.gov/

Table:

B19013 — Median Household Income

Geography:

Census Tract

⚠️ Census data is staged for later enrichment.

🔁 How to Reproduce the Data Pipeline
Step 1 — Download HMDA 2023 Modified LAR

Go to: [https://ffiec.cfpb.gov/data-publication/](https://ffiec.cfpb.gov/data-publication/)

Select Modified LAR

Choose year 2023

Download the .txt file (optionally include header)

Place the file in:

data/raw/hmda/

Step 2 — Set up Python environment
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt

Step 3 — Data Cleaning & Chunked Processing 

Because the HMDA file is too large to load into memory at once, it is processed in chunks.

Cleaning steps performed:

Read data in chunks of 200,000 rows

Standardize applicant_gender

Keep only Male and Female

Remove unknown / missing gender values

Validate income

Remove missing income

Remove negative or invalid income values

Validate loan amount

Remove missing loan amounts

De-duplicate applications

Log data quality metrics per chunk

Cleaned outputs are written as parquet partitions:

data/clean/hmda/hmda_2023_parts/part_*.parquet


A data-quality log is generated:

outputs/dq_logs/dq_log_2023.csv

Step 4 — Build Analytics Layer 

Run the automated ETL pipeline:

python src/etl/build_analytics_2023.py


This script:

Reads cleaned parquet partitions

Builds an analytics-ready fact table

Creates dimension tables

Engineers features such as:

income_bucket (Low / Middle / High using quantiles)

approved (binary outcome)

dti_est (loan_amount / annual_income)

loan_risk_tier (proxy using interest rate)

Writes outputs to:

data/analytics/hmda/


Key outputs:

fact_loans_2023.parquet

dim_applicants.parquet

dim_income.parquet

dim_geography.parquet

dim_lenders.parquet

Aggregated bias metrics tables

🧪 Analysis Notebooks

All analysis notebooks assume the analytics layer exists locally.

Notebooks:

01_ingestion_cleaning.ipynb — HMDA chunked cleaning

02_summary_stats.ipynb — initial descriptive analysis

03_income_bucketing.ipynb — income distribution & bucketing

05_loan_purpose_control.ipynb — loan-purpose–controlled aggregation

06_bias_analysis_week3.ipynb — statistical bias analysis

🔐 Data Privacy & Size Considerations

No personally identifiable information (PII) is included

Data is public but very large

GitHub repository contains:

code

documentation

reproducibility instructions

Data is regenerated locally by design
