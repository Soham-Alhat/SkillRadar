import re
import os
import spacy
from supabase import create_client
from collections import Counter
from datetime import datetime, timezone


SKILL_KEYWORDS = {
    "python", "sql", "excel", "power bi", "tableau", "r", "java", "scala",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "mongodb", "mysql", "postgresql", "sqlite", "oracle", "redis",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux",
    "spark", "hadoop", "airflow", "kafka", "etl", "data pipeline",
    "statistics", "data analysis", "data visualization", "data modeling",
    "regression", "classification", "clustering", "neural network",
    "api", "rest api", "fastapi", "flask", "django", "streamlit",
    "powerpoint", "communication", "problem solving",
    "scrapy", "selenium", "beautifulsoup", "opencv", "langchain"
}

nlp = spacy.load("en_core_web_sm")


def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        try:
            import toml, pathlib
            p = pathlib.Path(__file__).parent.parent / "dashboard" / ".streamlit" / "secrets.toml"
            s = toml.load(p)
            url = s.get("SUPABASE_URL", "")
            key = s.get("SUPABASE_KEY", "")
        except Exception:
            pass
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY not found.")
    return create_client(url, key)


def extract_skills(text: str) -> list:
    if not text:
        return []
    text_lower = text.lower()
    found = set()
    for skill in SKILL_KEYWORDS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return list(found)


def process_all_jobs():
    supa = get_supabase()

    # read all jobs from Supabase
    print("Fetching jobs from Supabase...")
    all_jobs = []
    page_size = 1000
    offset    = 0

    while True:
        resp = supa.table("jobs").select(
            "id, title, description, role"
        ).range(offset, offset + page_size - 1).execute()

        batch = resp.data
        if not batch:
            break
        all_jobs.extend(batch)
        offset += page_size
        if len(batch) < page_size:
            break

    print(f"Fetched {len(all_jobs)} jobs from Supabase")

    all_skills     = []
    role_skill_map = {}
    updated        = 0

    # extract skills and update each job row
    print("Extracting skills...")
    update_batch = []

    for job in all_jobs:
        description = job.get("description", "")
        title       = job.get("title", "")
        role        = job.get("role", "unknown")
        combined    = f"{title} {description}"

        extracted = extract_skills(combined)

        update_batch.append({
            "id"              : job["id"],
            "extracted_skills": extracted
        })

        all_skills.extend(extracted)

        if role not in role_skill_map:
            role_skill_map[role] = []
        role_skill_map[role].extend(extracted)

        updated += 1

        # push updates in batches of 100
        if len(update_batch) == 100:
            supa.table("jobs").upsert(update_batch).execute()
            update_batch = []
            print(f"  Updated {updated} jobs so far...")

    # push remaining
    if update_batch:
        supa.table("jobs").upsert(update_batch).execute()

    print(f"Processed {updated} jobs total")

    # calculate skill frequencies
    total        = updated
    skill_counts = Counter(all_skills)

    # clear and rewrite skills table
    print("Updating skills table in Supabase...")
    supa.table("skills").delete().gt("id", 0).execute()

    skill_rows = []
    for skill, count in skill_counts.most_common():
        skill_rows.append({
            "skill"     : skill,
            "count"     : count,
            "percentage": round(count / total * 100, 1),
            "updated_at": str(datetime.now(timezone.utc))
        })

    # insert in batches of 50
    for i in range(0, len(skill_rows), 50):
        supa.table("skills").insert(skill_rows[i:i+50]).execute()

    print(f"\nTop 10 skills:")
    for skill, count in skill_counts.most_common(10):
        print(f"  {skill:<25} {count} jobs  ({round(count/total*100,1)}%)")

    print("\nDone. Supabase fully updated.")


if __name__ == "__main__":
    process_all_jobs()