# Detailed quality report

## Scope and evidence

The original version 1 CSV contains 1,500 rows and 25 columns. All original bytes are preserved. The main cleaned dataset contains 1,500 rows and 40 columns; it has no silently dropped observations. Detailed reproducible evidence is in quality_checks.csv, column_profile.csv, row_issue_log.csv, before_after_examples.csv and summary.json. A separate local PostgreSQL execution matched every raw field and all 40 processed columns to the Python results.

## Missing values and types

Across 37,500 source cells, there are zero blanks after whitespace checks and zero conventional null placeholders (NA, N/A, NULL, None, NaN or Unknown). There are zero exact duplicate source rows and zero duplicate job IDs. Global and Remote are meaningful source labels rather than missing-value placeholders. No imputation is performed.

Nine source columns are interpreted as integers before binary conversion, including experience years, salary bounds, demand score, posting year/month and three indicators. Four source columns are numeric: annual salary, AI premium, growth and benefits score. The indicators become booleans in processed tables. The remaining 12 source columns are text. Raw PostgreSQL fields stay as text so source strings survive ingestion. Every required number parses, the months are 1–12, years are 2025/2026, experience is nonnegative, salary bounds are positive and ordered, binary fields are 0/1, and documented score ranges pass.

## Findings and handling

| Finding | Affected jobs | Percent of 1,500 | Decision |
|---|---:|---:|---|
| Repeated skills within a job | 119 | 7.93% | Remove 120 repeated tokens within their own job; keep original strings in the raw layer. |
| Annual salary outside accompanying range | 288 | 19.20% | Retain all source fields; flag the conflict; separate validated salary is NULL; exclude from conservative salary view. |
| Experience label disagrees with years | 1,099 | 73.27% | Keep both fields and flag; agreement-based experience view has 401 records. |
| Salary-tier boundary disagreement | 61 | 4.07% | Retain original label and add a separate derived tier with explicit boundaries. |
| Global geography is not a country | 82 | 5.47% | Keep listing and Global label; leave country code NULL; exclude from physical-country salary comparisons. |

The flags overlap. A total of 1,649 issue-log entries does not mean 1,649 different affected jobs. Zero source rows are dropped. The conservative salary subset has 1,212 rows, and combining salary consistency with physical-country eligibility yields 1,155 rows. These subsets are optional analysis views, not replacements for the full cleaned table.

## Actual before and after examples

- AIJOB0004 contains SQL twice in required_skills. The cleaned list contains it once. The first spelling and source order are retained.
- AIJOB0003 has annual_salary_usd=360000, salary_min_usd=160000 and salary_max_usd=300000. All original values remain; salary_range_consistent=false and annual_salary_usd_validated is NULL. No clipping or midpoint substitution is justified.
- AIJOB0002 is Senior (6-9 yrs) with years_of_experience=2. Both fields remain and experience_consistent=false.
- AIJOB0060 has annual salary 100000 and source tier Entry (<$100k). The separate derived tier is Mid ($100-150k). Of 61 boundary disagreements, 29 occur at 100000, 25 at 150000 and 7 at 200000. This is a documented boundary interpretation, not an independent verification of salary.

## Explicit processing decisions

Skills are split on the original pipe delimiter, whitespace is normalized, and matching ignores case within each job. Semantically different source skill labels are not merged through an invented alias map. The 9,428 unique job-skill pairs cover 93 lowercase skill keys.

The original country labels remain available. USA, UK and UAE receive expanded names and ISO codes US, GB and AE. Global receives no physical-country code. The experience_group derives only from the original label. The derived posting_period is the first day of the source year/month for grouping; it is not an observed exact posting date.

Derived salary tiers use these non-overlapping rules: x<100000; 100000<=x<150000; 150000<=x<200000; 200000<=x<=300000; x>300000. Original salary_tier is retained. Original annual salary is also retained even when the separate validated field is NULL. The range check is deliberately conservative because source documentation does not establish whether the accompanying bounds describe an individual posting or a general role benchmark.

## Critical and recoverable conditions

Critical failures stop the pipeline clearly: changed pinned source checksum, changed schema, missing or duplicated job ID, invalid required numeric values, invalid integer/binary values, nonpositive salaries, reversed bounds, invalid period, unsupported categories or scores outside documented scales. These do not lead to silent record deletion. The original source file remains untouched. The pgAdmin transaction rolls back on processing failure.

Recoverable conditions are addressed through explicit normalization, separate derived fields or flags. In this version those include repeated skills, salary and experience conflicts, tier boundaries and Global scope. Optional missing salary values in a future dataset would require a reviewed missing-value policy; this pinned version has none and performs no imputation. No unsupported salary, experience, education or score value is fabricated.

## Provenance and interpretation limits

The publisher describes the dataset as a compilation of salary reports and market research. The file lacks employer names, original posting URLs, source-level citations per row and full job descriptions. Its row-level provenance is not independently verified. Course acceptability under the real-world-data requirement should be confirmed with the mentor; the package does not establish that these are raw scraped job postings. Source scores and market-growth claims are not independently validated. Sample summaries must not be presented as verified market benchmarks or causal findings.

This is structured CSV data. Saving this table as JSON would not satisfy the separate format requirement. Its normalized skills table and analysis subsets do not count as additional distinct source datasets.
