import os
import duckdb

CLEAN_PARTS_GLOB = "data/clean/hmda/hmda_2023_parts/part_*.parquet"
OUT_DIR = "data/analytics/hmda"
os.makedirs(OUT_DIR, exist_ok=True)

con = duckdb.connect(database=":memory:")

# FACT TABLE: one row per loan application (analysis-ready)
con.execute(f"""
CREATE OR REPLACE TABLE fact_loans AS
SELECT
  activity_year::INTEGER AS activity_year,
  lei,
  loan_type,
  loan_purpose,
  state_code,
  county_code,
  census_tract,

  applicant_gender,
  income::DOUBLE AS income_k,
  (income::DOUBLE) * 1000 AS income_usd,

  loan_amount::DOUBLE AS loan_amount,
  interest_rate::DOUBLE AS interest_rate,
  approved::INTEGER AS approved,

  -- Income bucket (from your quantiles)
  CASE
    WHEN income::DOUBLE < 72 THEN 'Low'
    WHEN income::DOUBLE < 141 THEN 'Middle'
    ELSE 'High'
  END AS income_bucket,

  -- Starter risk tier (simple; can refine later)
  CASE
    WHEN interest_rate IS NULL THEN 'Unknown'
    WHEN interest_rate < 5 THEN 'LowRisk'
    WHEN interest_rate < 8 THEN 'MediumRisk'
    ELSE 'HighRisk'
  END AS loan_risk_tier,

  -- Very rough DTI proxy: loan_amount / annual_income
  CASE
    WHEN income IS NULL OR income::DOUBLE <= 0 THEN NULL
    ELSE loan_amount / ((income::DOUBLE) * 1000)
  END AS dti_est
FROM read_parquet('{CLEAN_PARTS_GLOB}')
WHERE applicant_gender IN ('Male','Female')
  AND income::DOUBLE BETWEEN 19 AND 765;
""")

# DIM TABLES
con.execute("CREATE OR REPLACE TABLE dim_applicants AS SELECT DISTINCT applicant_gender FROM fact_loans;")
con.execute("CREATE OR REPLACE TABLE dim_income AS SELECT DISTINCT income_bucket FROM fact_loans;")
con.execute("CREATE OR REPLACE TABLE dim_geography AS SELECT DISTINCT state_code, county_code, census_tract FROM fact_loans;")
con.execute("CREATE OR REPLACE TABLE dim_lenders AS SELECT DISTINCT lei FROM fact_loans;")

# AGG TABLE: ApprovalRate by gender/income/state
con.execute("""
CREATE OR REPLACE TABLE agg_gender_income_state AS
SELECT
  state_code,
  income_bucket,
  applicant_gender,
  COUNT(*) AS applications,
  AVG(approved) AS approval_rate
FROM fact_loans
GROUP BY 1,2,3;
""")

# AGG TABLE: GenderApprovalGap = male - female
con.execute("""
CREATE OR REPLACE TABLE gender_approval_gap AS
SELECT
  state_code,
  income_bucket,
  (MAX(CASE WHEN applicant_gender='Male' THEN approval_rate END)
   -
   MAX(CASE WHEN applicant_gender='Female' THEN approval_rate END)
  ) AS gender_approval_gap
FROM agg_gender_income_state
GROUP BY 1,2;
""")

# EXPORT (Parquet)
con.execute(f"COPY fact_loans TO '{OUT_DIR}/fact_loans_2023.parquet' (FORMAT PARQUET);")
con.execute(f"COPY dim_applicants TO '{OUT_DIR}/dim_applicants.parquet' (FORMAT PARQUET);")
con.execute(f"COPY dim_income TO '{OUT_DIR}/dim_income.parquet' (FORMAT PARQUET);")
con.execute(f"COPY dim_geography TO '{OUT_DIR}/dim_geography.parquet' (FORMAT PARQUET);")
con.execute(f"COPY dim_lenders TO '{OUT_DIR}/dim_lenders.parquet' (FORMAT PARQUET);")
con.execute(f"COPY agg_gender_income_state TO '{OUT_DIR}/agg_gender_income_state.parquet' (FORMAT PARQUET);")
con.execute(f"COPY gender_approval_gap TO '{OUT_DIR}/gender_approval_gap.parquet' (FORMAT PARQUET);")

print("✅ Week 2 analytics outputs written to:", OUT_DIR)
