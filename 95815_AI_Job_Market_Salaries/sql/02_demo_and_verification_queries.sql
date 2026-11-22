-- Run one selected query at a time in pgAdmin to inspect each result grid.
-- 1. Completed ingestion and row reconciliation.
SELECT * FROM m2_ai_salaries.ingestion_summary;

-- 2. Raw original values: the raw columns are text and contain original strings.
SELECT * FROM m2_ai_salaries.raw_jobs ORDER BY source_row LIMIT 5;

-- 3. Database-computed issue counts and decisions.
SELECT * FROM m2_ai_salaries.quality_checks ORDER BY check_name;

-- 4. Actual before and after skill cleaning.
SELECT r.job_id, r.required_skills AS original_skills,
       c.required_skills AS cleaned_skills,c.duplicate_skill_tokens_removed
FROM m2_ai_salaries.raw_jobs r
JOIN m2_ai_salaries.cleaned_jobs c USING (job_id)
WHERE c.duplicate_skill_tokens_removed > 0 ORDER BY r.source_row LIMIT 10;

-- 5. Conflicting values are preserved and explicitly flagged.
SELECT job_id,annual_salary_usd,salary_min_usd,salary_max_usd,
       salary_range_consistent,annual_salary_usd_validated
FROM m2_ai_salaries.cleaned_jobs
WHERE NOT salary_range_consistent ORDER BY source_row LIMIT 10;

SELECT job_id,experience_level,years_of_experience,experience_consistent
FROM m2_ai_salaries.cleaned_jobs
WHERE NOT experience_consistent ORDER BY source_row LIMIT 10;

-- 6. Explicit salary-band boundary treatment.
SELECT job_id,annual_salary_usd,salary_tier AS source_tier,salary_tier_derived
FROM m2_ai_salaries.cleaned_jobs
WHERE NOT salary_tier_consistent ORDER BY source_row LIMIT 10;

-- 7. Relational types and constraints are added in the processed layer.
SELECT table_name,column_name,data_type
FROM information_schema.columns
WHERE table_schema='m2_ai_salaries'
AND table_name IN ('raw_jobs','cleaned_jobs')
AND column_name IN ('annual_salary_usd','posting_month','is_senior','country_iso2')
ORDER BY table_name,column_name;

-- 8. Normalized skills: one skill per job per row.
SELECT * FROM m2_ai_salaries.job_skills ORDER BY job_id,skill_key LIMIT 15;

-- 9. Row-level issue log.
SELECT * FROM m2_ai_salaries.row_issue_log ORDER BY source_row,issue LIMIT 20;

-- 10. Simple downstream demonstration; these are sample summaries, not
-- verified market benchmarks or causal salary premiums.
SELECT country_name,COUNT(*) AS sample_jobs,
       ROUND(AVG(annual_salary_usd_validated),2) AS sample_mean_salary_usd
FROM m2_ai_salaries.country_salary_analysis_ready
GROUP BY country_name ORDER BY sample_jobs DESC;

SELECT skill_key,MIN(skill) AS display_name,COUNT(*) AS postings_mentioning_skill
FROM m2_ai_salaries.job_skills GROUP BY skill_key
ORDER BY postings_mentioning_skill DESC,skill_key LIMIT 15;
