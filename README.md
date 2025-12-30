## Lending Bias Analysis using HMDA Data

---

## 📌 Project Overview
This project analyzes **gender-based disparities in U.S. mortgage lending** using the **Home Mortgage Disclosure Act (HMDA)** nationwide Loan/Application Register (LAR) data.

The objective is to quantify differences in **loan approval rates, loan amounts, interest rates, and denial patterns** across gender while controlling for **income, geography, and loan characteristics**.

Due to the **large size and regulatory nature of HMDA data**, raw and processed datasets are **not stored in this GitHub repository**. Instead, this project focuses on **reproducible data engineering, cleaning, and feature-engineering pipelines**.

---

## 📊 Data Sources

### Primary Dataset
- **HMDA Modified Loan/Application Register (LAR)**
- Year used: **2023**
- Scope: **Nationwide**
- Format: **Pipe-delimited (.txt)**
- File size: ~2.5 GB
- Source
-HMDA (Home Mortgage Disclosure Act) Public Data: 
https://ffiec.cfpb.gov/data-publication/ 
- Census Demographics (Income, Race, Gender, Occupation): 
https://data.census.gov/ 

### Why data is not included
- HMDA LAR files exceed GitHub size limits
- Public HMDA data has distribution constraints
- Best practice is to version **code**, not large raw datasets

## Status
- Week 1: Data ingestion & cleaning ✅
- Week 2: ETL pipeline & analytics layer (local-first) ✅
- Week 3: Exploratory Data Analysis & Bias Measurement
- week 4: Predictive Modeling & Fairness Analysis

## How to Run
1. Create a Python virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Run ETL:
   python src/etl/build_analytics_2023.py

## Notes
- Raw data is not included due to size
- See docs/PROJECT_HANDOFF.md for full context
