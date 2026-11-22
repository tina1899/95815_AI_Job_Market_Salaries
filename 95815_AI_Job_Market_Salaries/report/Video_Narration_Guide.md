# Narration guide for the salaries dataset

Use about 60–75 seconds within the team's five-minute video. Record the verified AWS database ai_jobs_product, schema m2_ai_salaries. The loader has already been run successfully; show the saved script and use read-only verification queries for the demo. One or two presenters can cover the entire team demo.

| Time | Show | Say |
|---|---|---|
| 0–10 sec | Original Kaggle source page and original CSV | We used version 1 of AI Jobs Market Salaries, published by Syed Ali Taqi. The CSV has 1,500 rows and 25 columns, with salary, location, experience and skill fields. The publisher describes it as a compilation of reports and market research. |
| 10–25 sec | pgAdmin load script, then ingestion_summary | Our raw table preserves all source records as text. This SQL loads the records and creates a separate processed table. Here are 1,500 raw rows, 1,500 cleaned rows and 9,428 normalized job-skill pairs. |
| 25–40 sec | Original and cleaned skill strings for AIJOB0004 | This source row repeats SQL in its skill list. We removed repeated skills within a job, eliminating 120 repeated tokens across 119 jobs. |
| 40–55 sec | Salary and experience conflict queries | We flagged 288 salaries outside the accompanying ranges and 1,099 experience-band conflicts. We kept the source values and added flags instead of guessing corrections. |
| 55–70 sec | quality_checks, row_issue_log and processed views | These checks and the row-level log document our decisions. No source rows were dropped. Separate views identify records suitable for conservative salary and country comparisons. |

The AWS load has been verified from the supplied pgAdmin screenshots. Show those actual results or rerun the read-only verification queries; do not rerun the loader in the populated schema. The full team video also needs the other data sources and their ingestion/cleaning evidence.

## Ready to read narration

For the salaries dataset, I used AI Jobs Market 2025–2026 Salaries from Kaggle. The original CSV has 1,500 records and 25 columns. I loaded it into our AWS PostgreSQL instance, in database ai_jobs_product, and kept raw and cleaned tables separate. All 1,500 jobs were retained. I checked missing values, duplicates, data types and consistency. There were no missing source cells or duplicate job IDs. I removed 120 repeated skill tokens across 119 jobs, giving 9,428 unique job-skill pairs. Here, SQL appears twice in the original list and once after cleaning. I also flagged 288 salary-range conflicts and 1,099 experience conflicts, keeping the source values instead of guessing corrections. The quality checks and issue log document those decisions. The publisher describes the dataset as a compilation of reports and market research, so its row-level provenance remains a limitation.
