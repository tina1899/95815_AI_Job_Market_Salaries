# Salaries dataset contribution

Contributor: Tina Joshi, Group 2, Data Engineering 95-815.

This contribution covers source acquisition, a faithful raw layer, PostgreSQL ingestion, initial cleaning, normalization of job-skill pairs, quality checks, issue documentation, and Milestone 2 report/demo material for the salaries dataset.

The supplied pipeline was tested against local PostgreSQL 16.2 and compared with reproducible Python outputs. Tina then executed the SQL in the existing AWS RDS PostgreSQL database `ai_jobs_product`, schema `m2_ai_salaries`, through pgAdmin. The three provided pgAdmin screenshots verify the AWS results. The assistant did not connect directly to Tina's AWS database; local validation and user-provided cloud evidence are identified separately.

The repository contains only the salaries contribution. It does not claim authorship or implementation of the team's layoffs or Adzuna pipelines, a completed cross-source join, the final video, or the final combined report. All 1,500 source records remain available, including unresolved conflicts and source limitations.
