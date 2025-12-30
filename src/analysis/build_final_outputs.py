from pathlib import Path
import duckdb

FACT = Path("data/analytics/hmda/fact_loans_2023.parquet")
OUT_DIR = Path("outputs/final")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    con = duckdb.connect(database=":memory:")

    # 1) Loan amount + interest rate gaps for APPROVED loans (controlled)
    con.execute(f"""
        COPY (
            WITH base AS (
                SELECT
                    state_code,
                    income_bucket,
                    TRIM(CAST(loan_purpose AS VARCHAR)) AS loan_purpose,
                    applicant_gender,
                    COUNT(*) AS approvals_count,
                    quantile_cont(loan_amount, 0.5) AS median_loan_amount,
                    quantile_cont(interest_rate, 0.5) AS median_interest_rate
                FROM read_parquet('{FACT.as_posix()}')
                WHERE approved = 1
                  AND applicant_gender IN ('Male','Female')
                  AND loan_amount IS NOT NULL
                  AND interest_rate IS NOT NULL
                  AND state_code IS NOT NULL
                  AND income_bucket IS NOT NULL
                  AND loan_purpose IS NOT NULL
                  AND TRIM(CAST(loan_purpose AS VARCHAR)) != '5'
                GROUP BY 1,2,3,4
            ),
            piv AS (
                SELECT
                    state_code,
                    income_bucket,
                    loan_purpose,
                    MAX(CASE WHEN applicant_gender='Male' THEN median_loan_amount END) AS median_loan_amount_male,
                    MAX(CASE WHEN applicant_gender='Female' THEN median_loan_amount END) AS median_loan_amount_female,
                    MAX(CASE WHEN applicant_gender='Male' THEN median_interest_rate END) AS median_interest_rate_male,
                    MAX(CASE WHEN applicant_gender='Female' THEN median_interest_rate END) AS median_interest_rate_female,
                    MAX(CASE WHEN applicant_gender='Male' THEN approvals_count END) AS approvals_male,
                    MAX(CASE WHEN applicant_gender='Female' THEN approvals_count END) AS approvals_female
                FROM base
                GROUP BY 1,2,3
            )
            SELECT
                *,
                (median_loan_amount_male - median_loan_amount_female) AS loan_amount_gap_male_minus_female,
                (median_interest_rate_male - median_interest_rate_female) AS interest_rate_gap_male_minus_female
            FROM piv
        )
        TO '{(OUT_DIR / "gaps_amount_rate_state_income_purpose.parquet").as_posix()}'
        (FORMAT PARQUET);
    """)

    # 2) State hotspots summary from significant cases 
    SIG = Path("data/analytics/hmda/gender_bias_significant_cases.parquet")
    if SIG.exists():
        con.execute(f"""
            COPY (
                SELECT
                    state_code,
                    COUNT(*) AS significant_groups,
                    AVG(approval_gap_male_minus_female) AS avg_approval_gap_male_minus_female,
                    AVG(disparate_impact) AS avg_disparate_impact,
                    SUM(CASE WHEN approval_gap_male_minus_female > 0 THEN 1 ELSE 0 END) AS male_favored_groups,
                    SUM(CASE WHEN approval_gap_male_minus_female < 0 THEN 1 ELSE 0 END) AS female_favored_groups
                FROM read_parquet('{SIG.as_posix()}')
                GROUP BY 1
                ORDER BY significant_groups DESC
            )
            TO '{(OUT_DIR / "state_hotspots_significant_groups.parquet").as_posix()}'
            (FORMAT PARQUET);
        """)

    # 3) Lender bias scoreboard (from fact table + dim_lenders join if possible)
   
   
    con.execute(f"""
        CREATE VIEW fact AS
        SELECT * FROM read_parquet('{FACT.as_posix()}');
    """)

   
    # We'll create a lender_id that uses whichever exists.
    con.execute("""
       CREATE VIEW fact_lender AS
SELECT
    state_code,
    income_bucket,
    TRIM(CAST(loan_purpose AS VARCHAR)) AS loan_purpose,
    applicant_gender,
    approved::INT AS approved,
    TRIM(CAST(lei AS VARCHAR)) AS lender_id
FROM fact
WHERE applicant_gender IN ('Male','Female')
  AND state_code IS NOT NULL
  AND income_bucket IS NOT NULL
  AND loan_purpose IS NOT NULL
  AND TRIM(CAST(loan_purpose AS VARCHAR)) != '5'
  AND lei IS NOT NULL;
    """)

    # Controlled lender gaps (filter small samples)
    con.execute(f"""
        COPY (
            WITH base AS (
                SELECT
                    lender_id,
                    state_code,
                    income_bucket,
                    loan_purpose,
                    applicant_gender,
                    COUNT(*) AS applications,
                    AVG(approved)::DOUBLE AS approval_rate
                FROM fact_lender
                WHERE lender_id IS NOT NULL
                GROUP BY 1,2,3,4,5
            ),
            piv AS (
                SELECT
                    lender_id,
                    state_code,
                    income_bucket,
                    loan_purpose,
                    MAX(CASE WHEN applicant_gender='Male' THEN approval_rate END) AS approval_rate_male,
                    MAX(CASE WHEN applicant_gender='Female' THEN approval_rate END) AS approval_rate_female,
                    MAX(CASE WHEN applicant_gender='Male' THEN applications END) AS applications_male,
                    MAX(CASE WHEN applicant_gender='Female' THEN applications END) AS applications_female
                FROM base
                GROUP BY 1,2,3,4
            ),
            filtered AS (
                SELECT *
                FROM piv
                WHERE applications_male >= 50 AND applications_female >= 50
                  AND approval_rate_male IS NOT NULL AND approval_rate_female IS NOT NULL
            )
            SELECT
                lender_id,
                COUNT(*) AS controlled_groups,
                AVG(approval_rate_male - approval_rate_female) AS avg_gap_male_minus_female,
                AVG(approval_rate_female / NULLIF(approval_rate_male,0)) AS avg_disparate_impact,
                SUM(CASE WHEN (approval_rate_male - approval_rate_female) > 0 THEN 1 ELSE 0 END) AS male_favored_groups,
                SUM(CASE WHEN (approval_rate_male - approval_rate_female) < 0 THEN 1 ELSE 0 END) AS female_favored_groups
            FROM filtered
            GROUP BY 1
            HAVING COUNT(*) >= 10
            ORDER BY ABS(AVG(approval_rate_male - approval_rate_female)) DESC
        )
        TO '{(OUT_DIR / "lender_bias_scoreboard.parquet").as_posix()}'
        (FORMAT PARQUET);
    """)

    print("✅ Wrote final artifacts to:", OUT_DIR.resolve())

if __name__ == "__main__":
    main()
