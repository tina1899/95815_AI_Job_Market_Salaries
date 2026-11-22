"""Reproduce initial cleaning and quality evidence for Kaggle dataset version 1.

Run from any directory: python scripts/clean_and_profile.py
Only the cleaned/ and quality/ outputs are replaced. Raw files are never edited.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "raw/ai_jobs_market_2025_2026.csv"
SOURCE_SHA256 = "6ae7bc7bf724250cd8c977f86b620128318070a23cb0b17340e58d2321f7864e"
INTEGER_COLUMNS = ["years_of_experience", "salary_min_usd", "salary_max_usd", "demand_score", "posting_year", "posting_month", "is_senior", "is_remote_friendly", "is_llm_role"]
DECIMAL_COLUMNS = ["annual_salary_usd", "ai_salary_premium_pct", "demand_growth_yoy_pct", "benefits_score_10"]
SOURCE_COLUMNS = ["job_id", "job_title", "job_category", "experience_level", "years_of_experience", "education_required", "annual_salary_usd", "salary_min_usd", "salary_max_usd", "city", "country", "remote_work", "company_size", "industry", "required_skills", "ai_salary_premium_pct", "demand_score", "demand_growth_yoy_pct", "benefits_score_10", "posting_year", "posting_month", "is_senior", "is_remote_friendly", "is_llm_role", "salary_tier"]
TEXT_COLUMNS = [c for c in SOURCE_COLUMNS if c not in INTEGER_COLUMNS + DECIMAL_COLUMNS]
COUNTRIES = {"USA": ("United States", "US"), "UK": ("United Kingdom", "GB"), "UAE": ("United Arab Emirates", "AE"), "Australia": ("Australia", "AU"), "Canada": ("Canada", "CA"), "China": ("China", "CN"), "France": ("France", "FR"), "Germany": ("Germany", "DE"), "India": ("India", "IN"), "Japan": ("Japan", "JP"), "Netherlands": ("Netherlands", "NL"), "Singapore": ("Singapore", "SG"), "Switzerland": ("Switzerland", "CH"), "Global": ("Global", "")}


def tier_for(salary):
    # Explicit non-overlapping boundaries; keep the source tier alongside this field.
    if pd.isna(salary):
        return pd.NA
    if salary < 100000:
        return "Entry (<$100k)"
    if salary < 150000:
        return "Mid ($100-150k)"
    if salary < 200000:
        return "Upper-Mid ($150-200k)"
    if salary <= 300000:
        return "Senior ($200-300k)"
    return "Elite (>$300k)"


def normalize_skills(value):
    tokens = [re.sub(r"\s+", " ", x.strip()) for x in value.split("|") if x.strip()]
    unique, seen = [], set()
    for token in tokens:
        key = token.casefold()
        if key not in seen:
            unique.append(token)
            seen.add(key)
    return unique, len(tokens) - len(unique)


def run():
    (ROOT / "cleaned").mkdir(exist_ok=True)
    (ROOT / "quality").mkdir(exist_ok=True)
    raw = pd.read_csv(SOURCE, dtype=str, keep_default_na=False)
    checks, issues = [], []

    def check(name, affected, severity, decision, examples="", unit="rows", note=""):
        checks.append(dict(check_name=name, affected_count=int(affected), unit=unit,
                           severity=severity, status="PASS" if not affected else "REVIEW",
                           decision=decision, examples=examples, note=note))

    def critical(name, affected, message):
        check(name, affected, "critical", message)
        if affected:
            pd.DataFrame(checks).to_csv(ROOT / "quality/quality_checks.csv", index=False)
            raise ValueError(f"Critical validation failed: {name}: {affected}. {message}")

    actual_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    critical("source_checksum_mismatch", int(actual_hash != SOURCE_SHA256), "Stop if the supplied version 1 source bytes changed; do not overwrite raw data.")
    critical("source_schema_mismatch", int(list(raw.columns) != SOURCE_COLUMNS), "Stop on missing, additional, duplicated, or reordered source columns.")
    critical("missing_job_id", raw.job_id.str.strip().eq("").sum(), "Stop if a job cannot be identified.")
    critical("duplicate_job_id", raw.job_id.duplicated().sum(), "Stop on repeated job IDs rather than choosing an arbitrary record.")
    check("exact_duplicate_rows", raw.duplicated().sum(), "recoverable", "No duplicates found. Keep raw records; investigate before removing future repeated rows.")
    missing = raw.apply(lambda s: s.str.strip().eq("")).sum()
    check("missing_source_cells", missing.sum(), "recoverable", "No missing source cells found; no imputation performed.", unit="cells")
    null_tokens = raw.apply(lambda s: s.str.strip().str.casefold().isin(["na", "n/a", "null", "none", "nan", "unknown"])).sum()
    check("placeholder_null_source_cells", null_tokens.sum(), "recoverable", "No conventional placeholder nulls found. Global and Remote describe scope, not missing values.", unit="cells")
    clean = raw.copy()
    clean.insert(0, "source_row", range(1, len(raw) + 1))
    for column in INTEGER_COLUMNS + DECIMAL_COLUMNS:
        parsed = pd.to_numeric(raw[column], errors="coerce")
        critical(f"invalid_numeric_{column}", parsed.isna().sum(), "Stop on missing or unparseable required numeric values; retain the raw file.")
        if column in INTEGER_COLUMNS:
            critical(f"noninteger_{column}", (parsed % 1 != 0).sum(), "Stop instead of silently rounding source integers.")
            clean[column] = parsed.astype("int64")
        else:
            clean[column] = parsed.astype("float64")
    for column in TEXT_COLUMNS:
        clean[column] = clean[column].str.strip()
    check("outer_whitespace_cells", sum((raw[c] != clean[c]).sum() for c in TEXT_COLUMNS), "recoverable", "Trim outer whitespace in processed text; no source cells required it in this version.", unit="cells")
    for c in ["is_senior", "is_remote_friendly", "is_llm_role"]:
        critical(f"invalid_binary_{c}", (~clean[c].isin([0, 1])).sum(), "Stop if a binary indicator is not 0 or 1.")
        clean[c] = clean[c].astype(bool)
    critical("invalid_posting_month", (~clean.posting_month.between(1, 12)).sum(), "Stop on an invalid month.")
    critical("unexpected_posting_year", (~clean.posting_year.isin([2025, 2026])).sum(), "This pinned source version documents years 2025 and 2026.")
    critical("negative_experience_years", (clean.years_of_experience < 0).sum(), "Stop on negative required experience.")
    critical("nonpositive_salary", (clean[["annual_salary_usd", "salary_min_usd", "salary_max_usd"]] <= 0).any(axis=1).sum(), "Stop on nonpositive compensation values.")
    critical("reversed_salary_range", (clean.salary_min_usd > clean.salary_max_usd).sum(), "Stop if the lower salary bound exceeds the upper bound.")
    critical("invalid_demand_score", (~clean.demand_score.between(0, 100)).sum(), "Stop if a demand score lies outside its documented scale.")
    critical("invalid_benefits_score", (~clean.benefits_score_10.between(0, 10)).sum(), "Stop if a benefits score lies outside its documented scale.")
    critical("unknown_country_label", (~clean.country.isin(COUNTRIES)).sum(), "Review new country labels before mapping them.")
    critical("unknown_experience_label", (~clean.experience_level.isin(["Entry (0-2 yrs)", "Mid (3-5 yrs)", "Senior (6-9 yrs)", "Lead (10+ yrs)"])).sum(), "Stop if an experience label cannot be interpreted.")
    critical("unknown_work_arrangement", (~clean.remote_work.isin(["On-site", "Hybrid", "Fully Remote"])).sum(), "Stop if a work arrangement cannot be interpreted.")

    all_skills, repeated = [], []
    for job_id, value in zip(clean.job_id, clean.required_skills):
        skills, removed = normalize_skills(value)
        repeated.append(removed)
        for skill in skills:
            all_skills.append({"job_id": job_id, "skill_key": skill.casefold(), "skill": skill})
    clean["required_skills"] = ["|".join(normalize_skills(x)[0]) for x in raw.required_skills]
    clean["skill_count"] = [len(normalize_skills(x)[0]) for x in raw.required_skills]
    clean["duplicate_skill_tokens_removed"] = repeated
    clean["country_name"] = clean.country.map(lambda c: COUNTRIES[c][0])
    clean["country_iso2"] = clean.country.map(lambda c: COUNTRIES[c][1])
    clean["experience_group"] = clean.experience_level.str.split(" (", regex=False).str[0]
    # First-of-month is an explicitly derived period, not a claimed original posting day.
    clean["posting_period"] = pd.to_datetime(dict(year=clean.posting_year, month=clean.posting_month, day=1)).dt.strftime("%Y-%m-%d")
    clean["salary_tier_derived"] = clean.annual_salary_usd.map(tier_for)
    clean["salary_range_consistent"] = clean.annual_salary_usd.between(clean.salary_min_usd, clean.salary_max_usd)
    years = clean.years_of_experience
    clean["experience_consistent"] = ((clean.experience_group.eq("Entry") & years.between(0, 2)) | (clean.experience_group.eq("Mid") & years.between(3, 5)) | (clean.experience_group.eq("Senior") & years.between(6, 9)) | (clean.experience_group.eq("Lead") & (years >= 10)))
    clean["salary_tier_consistent"] = clean.salary_tier.eq(clean.salary_tier_derived)
    clean["country_is_specific"] = clean.country.ne("Global")
    clean["salary_analysis_ready"] = clean.salary_range_consistent
    clean["country_salary_analysis_ready"] = clean.salary_range_consistent & clean.country_is_specific
    clean["annual_salary_usd_validated"] = clean.annual_salary_usd.where(clean.salary_range_consistent)
    check("repeated_skills_within_job", (clean.duplicate_skill_tokens_removed > 0).sum(), "recoverable", "Remove repeated skill tokens within each job, retaining first spelling and source order.", "AIJOB0004: SQL appears twice; AIJOB0011: Cloud appears twice.", note=f"Removed {sum(repeated)} repeated tokens, preserving the raw skill strings.")
    check("annual_salary_outside_stated_range", (~clean.salary_range_consistent).sum(), "recoverable", "Retain all source salary values, flag the conflict, and set annual_salary_usd_validated to NULL. Exclude flagged rows from the conservative salary view.", "AIJOB0003: annual 360000; min 160000; max 300000.", note="The source does not resolve whether ranges are posting-specific or role benchmarks; do not clip or invent a correction.")
    check("experience_label_years_conflict", (~clean.experience_consistent).sum(), "recoverable", "Retain both fields and flag the conflict. Use experience-consistent records for analyses that rely on agreement.", "AIJOB0002: Senior (6-9 yrs), but years_of_experience is 2.")
    check("salary_tier_boundary_disagreement", (~clean.salary_tier_consistent).sum(), "recoverable", "Retain source salary_tier and add salary_tier_derived using explicitly documented boundaries.", "AIJOB0060: 100000 is labeled Entry (<$100k) in source.", note="Derived tiers use <100k; 100k to <150k; 150k to <200k; 200k to 300k inclusive; >300k. These boundaries are a processing decision.")
    check("global_geography_not_country", (~clean.country_is_specific).sum(), "recoverable", "Retain Global listings, leave country_iso2 empty/NULL, and exclude them from physical-country salary comparisons.")
    check("senior_indicator_disagreement", clean.is_senior.ne(clean.experience_group.isin(["Senior", "Lead"])).sum(), "recoverable", "Check source indicator against the source experience label; retain source values.")
    check("remote_indicator_disagreement", clean.is_remote_friendly.ne(clean.remote_work.isin(["Hybrid", "Fully Remote"])).sum(), "recoverable", "Check source indicator against source work arrangement; retain source values.")

    for _, row in clean.iterrows():
        job_id = row.job_id
        def issue(name, original, processed, action):
            issues.append({"job_id": job_id, "source_row": int(row.source_row), "issue": name, "severity": "recoverable", "original_value": original, "processed_value": processed, "action": action})
        if row.duplicate_skill_tokens_removed:
            issue("repeated_skills_within_job", raw.loc[row.source_row - 1, "required_skills"], row.required_skills, "Deduplicated repeated tokens within this job only.")
        if not row.salary_range_consistent:
            issue("annual_salary_outside_stated_range", f"annual={row.annual_salary_usd};min={row.salary_min_usd};max={row.salary_max_usd}", "annual_salary_usd_validated=NULL", "Kept original values; flagged; excluded from conservative salary view.")
        if not row.experience_consistent:
            issue("experience_label_years_conflict", f"{row.experience_level};years={row.years_of_experience}", "experience_consistent=false", "Kept both source values; excluded from agreement-based experience view.")
        if not row.salary_tier_consistent:
            issue("salary_tier_boundary_disagreement", row.salary_tier, row.salary_tier_derived, "Added a separate derived tier; original label retained.")
        if not row.country_is_specific:
            issue("global_geography_not_country", row.country, "country_iso2=NULL", "Retained listing; excluded from physical-country comparisons.")

    skills = pd.DataFrame(all_skills)
    issue_frame = pd.DataFrame(issues)
    check_frame = pd.DataFrame(checks)
    clean.to_csv(ROOT / "cleaned/ai_jobs_market_cleaned.csv", index=False, na_rep="")
    skills.to_csv(ROOT / "cleaned/job_skills.csv", index=False)
    clean.loc[clean.salary_analysis_ready].to_csv(ROOT / "cleaned/salary_analysis_ready.csv", index=False, na_rep="")
    check_frame.to_csv(ROOT / "quality/quality_checks.csv", index=False)
    issue_frame.to_csv(ROOT / "quality/row_issue_log.csv", index=False)
    pd.DataFrame({"column": raw.columns, "missing_cells": missing.values, "placeholder_null_cells": null_tokens.values, "distinct_values": raw.nunique().values, "processed_type": [str(clean[c].dtype) for c in raw.columns]}).to_csv(ROOT / "quality/column_profile.csv", index=False)
    before_after = raw.loc[raw.job_id.isin(["AIJOB0002", "AIJOB0003", "AIJOB0004", "AIJOB0011", "AIJOB0060"])].merge(clean[["job_id", "required_skills", "salary_range_consistent", "experience_consistent", "salary_tier_derived", "salary_tier_consistent", "annual_salary_usd_validated"]], on="job_id", suffixes=("_original", "_cleaned"))
    before_after.to_csv(ROOT / "quality/before_after_examples.csv", index=False, na_rep="")
    summary = {
        "dataset_version": 1, "raw_sha256": actual_hash, "raw_rows": len(raw), "source_columns": len(raw.columns), "cleaned_rows": len(clean), "cleaned_columns": len(clean.columns),
        "missing_cells": int(missing.sum()), "placeholder_null_cells": int(null_tokens.sum()), "duplicate_rows": int(raw.duplicated().sum()), "duplicate_ids": int(raw.job_id.duplicated().sum()),
        "rows_with_repeated_skills": int((clean.duplicate_skill_tokens_removed > 0).sum()), "removed_skill_tokens": int(sum(repeated)), "raw_skill_tokens": int(len(skills) + sum(repeated)), "job_skill_pairs": len(skills), "unique_skill_keys": int(skills.skill_key.nunique()),
        "salary_range_conflicts": int((~clean.salary_range_consistent).sum()), "experience_conflicts": int((~clean.experience_consistent).sum()), "tier_boundary_disagreements": int((~clean.salary_tier_consistent).sum()),
        "global_rows": int((~clean.country_is_specific).sum()), "salary_analysis_rows": int(clean.salary_analysis_ready.sum()), "country_salary_analysis_rows": int(clean.country_salary_analysis_ready.sum()), "experience_consistent_rows": int(clean.experience_consistent.sum()), "row_issue_log_entries": len(issue_frame),
        "first_period": clean.posting_period.min(), "last_period": clean.posting_period.max(), "role_count": int(clean.job_title.nunique()), "country_label_count": int(clean.country.nunique()), "actual_country_count": int(clean.loc[clean.country_is_specific, "country"].nunique()),
        "critical_checks_failed": int(((check_frame.severity == "critical") & (check_frame.affected_count > 0)).sum()), "raw_records_dropped": 0,
        "source_provenance_status": "Publisher says compiled from salary reports and job-market research; row-level original postings are not independently verified.",
        "postgresql_user_database_status": "Python processing does not connect to a database. See evidence/aws_ingestion_verification.json for the separately verified AWS load."
    }
    (ROOT / "quality/summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != actual_hash:
        raise RuntimeError("Raw source changed during processing")
    print(json.dumps(summary, indent=2))
    return raw, clean, skills, check_frame, issue_frame, summary


if __name__ == "__main__":
    run()
