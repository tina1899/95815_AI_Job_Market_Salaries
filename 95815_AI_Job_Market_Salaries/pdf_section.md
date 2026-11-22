# AI Jobs Salaries Data Source

Source: https://www.kaggle.com/datasets/alitaqishah/ai-jobs-market-2025-2026-salaries

## Source and relevance

AI Jobs Market 2025–2026 Salaries, published by Syed Ali Taqi, supports skills-by-role and pay-by-location questions. Version 1 has 1,500 records, 25 columns and a 383,900-byte CSV. Fields include role, salary, city/country, experience, education and pipe-separated skills. Recorded periods span January 2025–March 2026, with 25 role titles and 14 country labels, including Global. The publisher reports CC0 licensing and describes a compilation of salary reports and market research; row-level original postings are not independently verified.

## Storage and ingestion

Original CSV/ZIP files, metadata and checksums preserve the source. We loaded the dataset into Amazon RDS PostgreSQL instance de-postgres in us-east-2, database ai_jobs_product, schema m2_ai_salaries. Separate raw_jobs, cleaned_jobs and job_skills tables preserve raw text before typed processing. Executed pgAdmin results confirm 1,500 raw rows, 1,500 cleaned rows and 9,428 job-skill pairs. The quality checks and before/after example also match the reproducible pipeline. PostgreSQL supports comparisons and joins; original files and code are supplied for the team’s shared folder.

## Quality checks and cleaning

All 25 columns were checked. There were zero blank cells, placeholder nulls, duplicate IDs or full duplicate records. Numeric parsing, date bounds, binary values and score ranges passed. No imputation was performed; all 1,500 jobs remain.

| Finding | Jobs | Handling |
|---|---:|---|
| Repeated skill tokens | 119 | Remove 120 repeated tokens; keep first spelling/order. |
| Annual salary outside stated range | 288 | Retain source values; flag; separate validated salary is NULL. |
| Experience label disagrees with years | 1,099 | Retain both fields and flag the conflict. |
| Salary tier boundary disagreement | 61 | Retain source tier and add an explicit derived tier. |
| Global is not a physical country | 82 | Retain listing; country code NULL; exclude country comparison. |

The skill table has 9,428 unique job-skill pairs. Conservative views contain 1,212 salary-consistent records and 1,155 records also eligible for physical-country comparisons. The row log has 1,649 entries because issues overlap. Critical schema, ID or numeric failures stop processing; recoverable issues remain flagged.

## Interpretation and limits

Ranges may be role benchmarks rather than individual posting bounds, so salaries were not clipped. Derived tiers use <100k, 100k–<150k, 150k–<200k, 200k–300k inclusive and >300k. Original labels remain. Confirm source provenance with the mentor; the file lacks original URLs and full descriptions. Source scores lack independently verified methods. This is one structured dataset; its skill table and subsets are processing outputs, and a separate semi-structured/unstructured source is still required.
