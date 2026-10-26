from services.job_connectors import JobListing, SearchFilters
from models.job import Job
from models.application_profile import ApplicationProfile
from datetime import datetime


def calculate_suitability(job: Job, profile: ApplicationProfile) -> dict:
    """
    Calculate a suitability score for a job against the user's profile.

    Returns a dict with:
    - score: int (0-100)
    - factors: dict of matching factors
    - missing: list of mandatory requirements not met
    - explanation: human-readable summary
    """

    factors = {}
    missing = []
    score = 0
    max_score = 100

    # 1. Skills match (30 points max)
    job_skills = _extract_skills(job.description or "")
    profile_skills = _extract_skills(profile.skills or "")
    skills_match = _calculate_skills_match(job_skills, profile_skills)
    skills_points = round(skills_match * 30)
    score += skills_points
    factors["skills_match"] = {
        "score": skills_points,
        "max": 30,
        "matched": profile_skills,
        "job_requirements": job_skills,
        "match_percentage": round((len(profile_skills) / max(len(job_skills), 1)) * 100) if job_skills else 100,
    }

    # 2. Qualification requirements (25 points max)
    qual_points, qual_missing = _calculate_qualification_points(
        job.description or "", profile
    )
    score += qual_points
    factors["qualifications"] = {
        "score": qual_points,
        "max": 25,
        "matched": _extract_qualifications(job.description or ""),
        "missing": qual_missing,
    }
    missing.extend(qual_missing)

    # 3. Experience level match (15 points max)
    exp_points, exp_missing = _calculate_experience_points(job.description or "", profile)
    score += exp_points
    factors["experience"] = {
        "score": exp_points,
        "max": 15,
        "matched": _extract_experience(job.description or ""),
        "missing": exp_missing,
    }
    missing.extend(exp_missing)

    # 4. Location match (15 points max)
    loc_points, loc_missing = _calculate_location_points(job.location or "", profile)
    score += loc_points
    factors["location"] = {
        "score": loc_points,
        "max": 15,
        "matched": _format_location(job.location),
        "missing": loc_missing,
    }
    missing.extend(loc_missing)

    # 5. Salary expectations (10 points max)
    sal_points, sal_missing = _calculate_salary_points(job.description or "", profile)

    # 6. Job type preference (5 points max)
    type_points = _calculate_job_type_points(job.description or "", profile)
    score += sal_points
    factors["salary"] = {
        "score": sal_points,
        "max": 10,
        "matched": _format_salary(job.salary),
        "missing": sal_missing,
    }
    missing.extend(sal_missing)

    # 6. Job type match (5 points max)
    type_points = _calculate_job_type_points(job.description or "", profile)
    score += type_points
    # Extract job type from description for display
    job_type_lower = (job.description or "").lower() if job.description else ""
    matched = []
    if profile.job_types:
        profile_type = profile.job_types.lower()
        if profile_type in job_type_lower:
            matched = [profile.job_types]
        else:
            # Check common variations
            type_map = {
                "full-time": ["full.time", "full time"],
                "part-time": ["part.time", "part time"],
                "contract": ["contract"],
                "apprenticeship": ["apprenticeship", "apprentice"],
            }
            for key, variations in type_map.items():
                if profile_type in variations:
                    if key in job_type_lower:
                        matched = [profile.job_types]
    factors["job_type"] = {
        "score": type_points,
        "max": 5,
        "matched": matched,
    }

    # Clamp score to 0-100
    score = max(0, min(100, score))

    # Determine missing requirements summary
    mandatory_missing = []
    optional_missing = []
    for r in missing:
        if isinstance(r, dict) and r.get("mandatory", True):
            mandatory_missing.append(r)
        elif isinstance(r, str):
            mandatory_missing.append(r)

    explanation_parts = []

    if factors["skills_match"]["score"] > 0:
        explanation_parts.append(
            f"Strong skills match: {factors['skills_match']['match_percentage']}% overlap"
        )
    if factors["qualifications"]["score"] > 0:
        q_miss = ", ".join(factors["qualifications"]["missing"][:3])
        explanation_parts.append(
            f"{'Missing' if q_miss else 'Meets'} qualification{'s: ' + q_miss if q_miss else ''}"
        )
    if factors["experience"]["score"] < 15:
        explanation_parts.append(
            f"Experience level may be partially mismatched"
        )
    if factors["location"]["score"] < 15:
        explanation_parts.append(
            f"Location outside preferred area"
        )

    explanation = ". ".join(explanation_parts) + "." if explanation_parts else "Good match overall."

    return {
        "score": score,
        "factors": factors,
        "missing": mandatory_missing,
        "explanation": explanation,
    }


def _extract_skills(text: str) -> list:
    """Extract skill keywords from text."""
    if not text:
        return []
    # Simple keyword extraction - take words from common skill terms
    import re
    # Look for capitalized skill-like terms or common tech terms
    skills = re.findall(r'\b(Python|Java|SQL|AWS|Docker|Kubernetes|Linux|Agile|Scrum|Git|JSON)\b', text, re.IGNORECASE)
    # Also split by common delimiters
    additional = [s.strip() for s in text.replace(",", " ").replace(";", " ").split() if s.strip()]
    all_skills = list(set([s.lower() for s in skills + additional]))
    return all_skills


def _extract_qualifications(text: str) -> list:
    """Extract qualification mentions from job description."""
    if not text:
        return []
    # Look for common qualification patterns
    import re
    quals = re.findall(r'\b(A-level|GCSE|BSc|MSc|PhD|C|CCNP|AWS|CISSP|ITIL)\b', text, re.IGNORECASE)
    return [q.lower() for q in quals]


def _extract_experience(text: str) -> str:
    """Extract experience requirements from description."""
    if not text:
        return ""
    import re
    Match = re.search(r'(\d+)\+?\s*(years|yrs?)\s*(experience|exp)', text, re.IGNORECASE)
    if Match:
        return f"{Match.group(1)} {Match.group(2)}"
    return ""


def _extract_skills_from_profile(skills_text: str) -> list:
    """Extract individual skills from profile text."""
    if not skills_text:
        return []
    return [s.strip().lower() for s in skills_text.replace(",", " ").split() if s.strip()]


def _calculate_skills_match(job_skills: list, profile_skills: list) -> float:
    """Calculate skills match percentage (0.0 - 1.0)."""
    if not job_skills and not profile_skills:
        return 1.0
    if not job_skills:
        return 0.5
    if not profile_skills:
        return 0.0

    # Check how many job requirements are covered by profile
    profile_set = set(profile_skills)
    matched = sum(1 for s in job_skills if s in profile_set)
    return matched / len(job_skills)


def _calculate_qualification_points(job_desc: str, profile: ApplicationProfile) -> tuple:
    """Calculate qualification match points (0-25) and list missing qualifications."""
    job_quals = _extract_qualifications(job_desc)
    profile_quals = set()

    # Check profile education field
    if profile.education:
        profile_quals.update(_extract_qualifications(profile.education))

    # Check if job qualifications are in profile
    matched = [q for q in job_quals if q.lower() in profile_quals]
    missing = [q for q in job_quals if q.lower() not in profile_quals]

    # Scoring: each matched qualification = 5 points, max 25
    points = min(25, len(matched) * 5)

    # Mark mandatory requirements as missing if job has many quals and profile has few
    mandatory_threshold = max(1, len(job_quals) // 2)
    missing_mandatory = missing[:max(0, len(job_quals) - len(matched))] if len(matched) < mandatory_threshold else []

    return points, [
        {"qualification": q, "mandatory": q in mandatory_missing}
        for q in missing
    ]


def _calculate_experience_points(job_desc: str, profile: ApplicationProfile) -> tuple:
    """Calculate experience match points (0-15) and list gaps."""
    job_exp_text = _extract_experience(job_desc)
    profile_exp_text = profile.experience or ""

    if not job_exp_text and not profile_exp_text:
        return 15, []  # No experience requirement = full points
    if not job_exp_text:
        return 0, []  # No requirement from job side

    # Extract years from job description
    import re
    job_years = int(re.search(r'(\d+)', job_exp_text).group(1)) if re.search(r'(\d+)', job_exp_text) else 0

    # Simple experience matching
    if profile_exp_text and job_years:
        profile_years = _extract_years_experience(profile_exp_text)
        diff = profile_years - job_years

        if diff >= job_years:
            return 15, []  # Profile has equal or more experience
        elif diff >= 0:
            # Profile has some experience but less than required
            points = round(15 * (profile_years / job_years))
            return points, [f"Requires {job_years - profile_years} more years experience"]
        else:
            # Profile has no relevant experience
            points = max(0, 15 - round(5 * (job_years - profile_years) / job_years))
            return points, [f"Requires {job_years} years experience; profile has {profile_years}"]

    return 5, ["Experience requirement"]  # Cannot determine match


def _extract_years_experience(exp_text: str) -> int:
    """Extract years of experience from profile text."""
    import re
    match = re.search(r'(\d+)\+?\s*(years|yrs?|experience)', exp_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


def _calculate_location_points(job_loc: str, profile: ApplicationProfile) -> tuple:
    """Calculate location match points (0-15) and list preferences not met."""
    profile_loc = profile.preferred_locations or ""
    profile_city = profile.city or ""

    if not job_loc and not profile_loc and not profile_city:
        return 15, []  # No location data = full points

    job_loc_lower = job_loc.lower()
    profile_loc_lower = profile_loc.lower()
    profile_city_lower = profile_city.lower()

    matched = []
    missing = []

    # Check if profile city/location is in job location
    if profile_city_lower in job_loc_lower:
        matched.append(profile_city)
    elif profile_loc_lower and profile_loc_lower in job_loc_lower:
        matched.append(profile_loc)
    else:
        # Check for partial matches (e.g., "Coventry" in "Coventry, Warwickshire")
        job_parts = job_loc_lower.split(",")
        profile_parts = profile_loc_lower.replace(" ", "").split(",")
        for p in profile_parts:
            if p.strip() and p.strip() in job_loc_lower:
                matched.append(p.strip())
                break

        if not matched:
            missing.append(f"Location: {job_loc} vs profile preference {profile_loc or profile_city or 'not set'}")

    # Scoring
    if len(matched) >= 2:
        points = 15  # Full match
    elif len(matched) == 1:
        points = 10  # Partial match
    elif not matched and (profile_loc or profile_city):
        points = 5  # Some preference set but not matching
    else:
        points = 0  # No location data

    return points, [m if isinstance(m, str) else m.get("qualification", "Location mismatch") for m in missing]


def _calculate_salary_points(job_sal: str, profile: ApplicationProfile) -> tuple:
    """Calculate salary match points (0-10)."""
    if not job_sal or not profile.salary_expectations:
        if not job_sal and not profile.salary_expectations:
            return 10, []  # Both unknown = full points
        if not job_sal:
            return 5, ["Salary not specified by employer"]  # Employer didn't specify
        return 5, ["Salary not in profile"]  # Profile doesn't have expectation

    # Simple comparison - check if profile expectation is within reasonable range
    # of job salary
    try:
        job_min = _extract_salary_min(job_sal)
        profile_exp = _extract_salary_exp(profile.salary_expectations)

        if job_min is None or profile_exp is None:
            return 5, ["Could not parse salary values"]

        # Profile expectation within 25% of job min = full points
        if profile_exp >= job_min * 0.75 and profile_exp <= job_min * 1.25:
            return 10, ["Salary meets expectations"]
        # Within 50% = partial points
        elif profile_exp >= job_min * 0.5:
            return 7, ["Salary slightly below expectations"]
        else:
            return 2, ["Salary significantly below expectations"]
    except (ValueError, TypeError):
        return 5, ["Could not parse salary values"]


def _extract_salary_min(salary_str: str) -> int:
    """Extract minimum salary from salary string."""
    import re
    match = re.search(r'£?(\d[\d,]*)', salary_str)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def _extract_salary_exp(salary_exp: str) -> int:
    """Extract expected salary number from profile text."""
    import re
    match = re.search(r'£?(\d[\d,]*)', salary_exp)
    if match:
        return int(match.group(1).replace(",", ""))
    # Try parsing "30000" or "30,000"
    match2 = re.search(r'(\d[\d,]*)', salary_exp)
    if match2:
        return int(match2.group(1).replace(",", ""))
    return None


def _calculate_job_type_points(job_desc: str, profile: ApplicationProfile) -> int:
    """Calculate job type match points (0-5)."""
    if not profile.job_types:
        return 3  # No preference = partial points

    job_type_lower = job_desc.lower() if job_desc else ""
    profile_type = profile.job_types.lower()

    # Check if profile job type appears in description
    if profile_type in job_type_lower:
        return 5

    # Check for common variations
    type_map = {
        "full-time": ["full.time", "full time"],
        "part-time": ["part.time", "part time"],
        "contract": ["contract"],
        "apprenticeship": ["apprenticeship", "apprentice"],
    }

    for key, variations in type_map.items():
        if profile_type in variations:
            if key in job_type_lower:
                return 5

    return 2  # Some awareness but no explicit match


def _format_location(loc: str) -> str:
    """Format location for display."""
    if not loc:
        return "Not specified"
    return loc


def _format_salary(sal: str) -> str:
    """Format salary for display."""
    if not sal:
        return "Not specified"
    return sal


# Convenience function for the search service
def get_suitable_jobs(db, profile: ApplicationProfile, min_score: int = 30) -> list:
    """Get jobs above minimum suitability score, with scoring."""
    from database.job_rep import JobRepository

    all_jobs = JobRepository.get_all_jobs(db)
    scored = []

    for job in all_jobs:
        result = calculate_suitability(job, profile)
        if result["score"] >= min_score:
            # Attach scoring to job object for template display
            job.suitability_score = result["score"]
            job.suitability_factors = result["factors"]
            job.missing_requirements = result["missing"]
            scored.append(job)

    # Sort by score descending
    scored.sort(key=lambda j: j.suitability_score or 0, reverse=True)
    return scored