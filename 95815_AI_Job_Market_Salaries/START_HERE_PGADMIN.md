# AI Jobs Salaries Milestone 2 package

Prepared for Tina Joshi, Group 2. This completes the local processing and evidence for the selected **one structured dataset**. The original CSV is unmodified. The SQL was validated in local PostgreSQL 16.2 and has now been run successfully by Tina in AWS RDS database ai_jobs_product, schema m2_ai_salaries. User-provided pgAdmin screenshots verify the expected counts, quality checks and before/after example. Access by teammates has not been verified.

## Completed AWS ingestion

The verified load contains 1,500 raw jobs, 1,500 cleaned jobs, 9,428 job-skill pairs and 1,649 issue-log entries. Do not rerun the load in the existing schema. Use sql/02_demo_and_verification_queries.sql for read-only inspection and the video. The following load instructions remain available for reproducing the pipeline in a fresh database.

## Reproduce in pgAdmin

1. Unzip this package. Open pgAdmin and connect to the database your team will use. Choose that database, then open Tools > Query Tool.
2. In Query Tool, open `sql/01_pgadmin_load_and_clean.sql` using the Open File button. Select the entire script, then click Execute (F5 in many pgAdmin installations).
3. The script creates schema `m2_ai_salaries`, loads all 1,500 original records, cleans them in SQL, builds the skill table and quality logs, then commits. It needs permission to CREATE in the selected database. It does not require superuser access or a local/server CSV path.
4. The final result must show raw_rows=1500, cleaned_rows=1500, job_skill_pairs=9428, removed_skill_tokens=120, salary_analysis_rows=1212, country_salary_analysis_rows=1155, experience_consistent_rows=401, row_issue_log_entries=1649.
5. Refresh the database's Schemas node. Expand m2_ai_salaries > Tables and Views. Open `sql/02_demo_and_verification_queries.sql` and run one selected query at a time to inspect original rows, quality counts and before/after examples.
6. Record these actual team-database results for the video and write down the actual shared PostgreSQL host/database/schema location. Do not include passwords in the PDF or video.

Run the load script once in a fresh target schema. Existing target tables cause it to stop instead of overwriting data. If you receive an error and pgAdmin says the transaction is aborted, execute `ROLLBACK;` first, then investigate the error. A missing CREATE permission must be resolved by the database owner. An existing raw_jobs table means this package was already loaded there; inspect its counts before doing anything else. The script contains no DROP or TRUNCATE statements.

## What is included

- `raw/ai_jobs_market_2025_2026.csv`: exact original CSV, 383,900 bytes, 1,500 rows and 25 columns.
- `raw/ai_jobs_market_2025_2026_original.zip`: untouched original Kaggle download.
- `raw/source_manifest.json` and Kaggle metadata snapshots: source/version/size/checksum evidence.
- `cleaned/ai_jobs_market_cleaned.csv`: all 1,500 jobs, typed values and 15 audit/derived columns, for 40 columns total. Conflicting source values are flagged rather than silently replaced.
- `cleaned/job_skills.csv`: 9,428 unique job-skill pairs representing 93 skill keys.
- `cleaned/salary_analysis_ready.csv`: 1,212 jobs satisfying the conservative salary-range consistency rule; this is a subset of the same dataset.
- `quality/`: per-column profile, aggregate quality checks, 1,649 row-level issue entries, before/after examples and summary JSON.
- `scripts/clean_and_profile.py`: reproducible cleaning script. `download_original.py` optionally checks or re-downloads the pinned original without overwriting an existing raw file.
- `notebooks/AI_Jobs_Salaries_Cleaning_Executed.ipynb`: executed notebook with original-data inspection, actual checks, before/after examples and reconciliation assertions.
- `sql/`: one self-contained pgAdmin load/clean script plus demonstration queries. Raw columns use text without source-discarding constraints. Keys, types and constraints are applied in processed tables.
- `report/`: editable M2 dataset section, detailed dictionary, quality report and a narration guide for this dataset's share of the team video.
- `evidence/`: actual local PostgreSQL validation and notebook execution results. Local execution is documented separately from the user-verified AWS load in evidence/aws_ingestion_verification.json.

## Actual quality findings

No blank cells, conventional placeholder nulls, duplicate job IDs, or full duplicate rows were found. No imputation was performed. Remove 120 repeated skill tokens affecting 119 jobs. Flag 288 annual salaries outside the accompanying minimum/maximum and 1,099 mismatches between experience labels and numeric years. Keep both conflicting source values. Add a separate derived salary tier for 61 boundary disagreements. Keep 82 Global listings while excluding them from physical-country salary comparisons. Main cleaned rows remain 1,500.

The salary-range check is a conservative consistency check, not proof that a salary is wrong: the publisher does not resolve whether the ranges are posting-specific or role-level benchmarks. Do not replace annual salaries with their range midpoint or clip them to a boundary.

## Reproduce locally with Python

Python is optional if you use the pgAdmin route. For the notebook/script route, install the packages listed in requirements.txt into your own Python environment. Run `python scripts/clean_and_profile.py` from the unzipped package. Alternatively, open the notebook and Run All; its path cell supports the package root or notebooks folder. Re-running the pipeline replaces only the generated cleaned and quality outputs and verifies the original SHA-256.

## Source and project scope

Source: https://www.kaggle.com/datasets/alitaqishah/ai-jobs-market-2025-2026-salaries

Publisher: Syed Ali Taqi. Version 1, released March 6, 2026. The actual source periods run January 2025 through March 2026. The file contains 25 role titles and 14 country labels, of which 13 are physical countries and one is Global. License reported by Kaggle: CC0 Public Domain.

The publisher describes the data as compiled from salary reports and job-market research. The file has no employer-name column, original posting URL or full job-description text, and the row-level collection method is not independently verified. Do not claim that this package proves these are raw scraped postings or verifies real-market salary benchmarks. Confirm provenance/acceptability with your mentor for the course's real-world-data requirement. Demand, growth, salary-premium and benefits scores are source-provided with no independently verified calculation method; keep them as supplied attributes rather than recomputing them from invented assumptions.

This CSV does not satisfy the semi-structured/unstructured requirement, and the cleaned subset and skills table do not count as distinct datasets. Teammates still need complementary real-world sources, meaningful integration for the final project, and the combined 3–4-page M2 PDF including updated M1 content, the running meeting-notes link, and an accessible narrated five-minute video link. The editable report section is for this dataset only. Update its storage/implementation status after your own pgAdmin execution.
