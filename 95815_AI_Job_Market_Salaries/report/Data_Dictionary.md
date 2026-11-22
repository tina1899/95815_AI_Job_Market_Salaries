# Data dictionary

Source: Kaggle dataset version 1. Original values remain in raw_jobs and the original CSV. Processed types below describe PostgreSQL cleaned_jobs.

| Source column | Processed type | Meaning |
|---|---|---|
| job_id | text | Unique job posting identifier |
| job_title | text | Specific AI/ML role title |
| job_category | text | Role category (AI Engineering, Data Science, etc.) |
| experience_level | text | Entry / Mid / Senior / Lead |
| years_of_experience | integer | Required years of experience |
| education_required | text | Minimum education level required |
| annual_salary_usd | numeric | Annual salary in USD |
| salary_min_usd | integer | Minimum salary range for role |
| salary_max_usd | integer | Maximum salary range for role |
| city | text | Job location city |
| country | text | Job location country |
| remote_work | text | On-site / Hybrid / Fully Remote |
| company_size | text | Startup / SME / Mid-size / Enterprise / Big Tech |
| industry | text | Industry sector of hiring company |
| required_skills | text | Pipe-separated list of required skills Repeated tokens are removed in the processed column; job_skills stores one skill per row. |
| ai_salary_premium_pct | numeric | Salary premium % vs non-AI equivalent role |
| demand_score | integer | Market demand score 0-100 for this role |
| demand_growth_yoy_pct | numeric | Year-over-year demand growth (%) |
| benefits_score_10 | numeric | Benefits package quality score (0-10) |
| posting_year | integer | Year job was posted (2025 or 2026) |
| posting_month | integer | Month job was posted |
| is_senior | boolean | 1 if Senior or Lead level role |
| is_remote_friendly | boolean | 1 if Hybrid or Fully Remote |
| is_llm_role | boolean | 1 if role involves LLM/GenAI work |
| salary_tier | text | Entry / Mid / Upper-Mid / Senior / Elite |

## Derived columns

| Column | PostgreSQL type | Meaning |
|---|---|---|
| source_row | bigint | Original data-row number, excluding the CSV header. |
| skill_count | integer | Number of unique skills in this job after deduplication. |
| duplicate_skill_tokens_removed | bigint | Repeated skill tokens removed within this job. |
| country_name | text | Expanded source labels, including United States, United Kingdom and United Arab Emirates. |
| country_iso2 | text | ISO alpha-2 country code; NULL/empty for Global. |
| experience_group | text | Entry, Mid, Senior or Lead, extracted from the original label. |
| posting_period | date | First day of the source year/month, for grouping only; not an observed posting day. |
| salary_tier_derived | text | Explicit boundaries: <100000; 100000 to <150000; 150000 to <200000; 200000 to 300000 inclusive; >300000. |
| salary_range_consistent | boolean | Whether annual_salary_usd falls within the accompanying salary_min_usd and salary_max_usd. |
| experience_consistent | boolean | Whether years_of_experience agrees with the numeric band in experience_level. |
| salary_tier_consistent | boolean | Whether the original salary-tier label matches the documented derived tier. |
| country_is_specific | boolean | False for Global; true for a physical country label. |
| salary_analysis_ready | boolean | Conservative eligibility rule, equal to salary_range_consistent. |
| country_salary_analysis_ready | boolean | Salary-range consistency plus a physical-country label. |
| annual_salary_usd_validated | numeric | Original annual salary for consistent ranges; NULL/empty for conflicting ranges. No salary is imputed or clipped. |

## Other tables

- `job_skills(job_id, skill_key, skill)` uses a primary key on `(job_id, skill_key)` and a foreign key to cleaned_jobs. skill_key is lowercase; display spelling is retained.
- `quality_checks` contains aggregate issue counts, severities and decisions.
- `row_issue_log` contains one entry per job and issue; jobs can have more than one issue. CSV logs additionally include original and processed values.
- `source_manifest` records the source link, pinned version, hash, download time and actual database load time.
- The full cleaned dataset retains 1,500 jobs. Salary and experience views are subsets and are not additional independent datasets.
