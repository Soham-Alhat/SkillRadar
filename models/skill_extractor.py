import re
import spacy
from pymongo import MongoClient
from collections import Counter
from datetime import datetime, timezone

# predefined skill keywords relevant to your target roles
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
    "excel", "powerpoint", "communication", "problem solving",
    "scrapy", "selenium", "beautifulsoup", "opencv", "langchain"
}

nlp = spacy.load("en_core_web_sm")


def extract_skills(text: str) -> list:
    if not text:
        return []

    text_lower = text.lower()
    found = set()

    for skill in SKILL_KEYWORDS:
        # word boundary match — "r" won't match inside "developer"
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)

    return list(found)

def process_all_jobs():
    client = MongoClient("mongodb://localhost:27017")
    db = client["skillradar"]
    jobs = db["jobs"]
    skills = db["skills"]

    all_skills = []
    role_skill_map = {} # This will track skills per each role soham lavdya keep in mind dont forget
    updated = 0

    for job in jobs.find():
        description = job.get("description", "")
        title = job.get("title", "")
        role = job.get("role", "unknown")
        combined = f"{title} {description}"

        extracted = extract_skills(combined)

        # update job document with extracted skills
        jobs.update_one(
            {"_id": job["_id"]},
            {"$set": {"extracted_skills": extracted}}
        )

        all_skills.extend(extracted)

        # Track skills per role
        if role not in role_skill_map:
            role_skill_map[role] = []
        role_skill_map[role].extend(extracted)

        updated += 1

    print(f"Processed {updated} jobs")

    # Calculate total jobs for percentage calculation
    total = updated
    # Count skill frequency across all jobs
    skill_counts = Counter(all_skills)

    # write to skills collection
    skills.drop()
    for skill, count in skill_counts.most_common():
        skills.insert_one({
            "skill": skill,
            "count": count,
            "percentage": round(count / updated * 100, 1),
            "updated_at": datetime.now(timezone.utc),
            "by_role" : {
                role : role_skill_map[role].count(skill)
                for role in role_skill_map
                if role_skill_map[role].count(skill) > 0
            }
        })

    print(f"Top 10 skills in market right now:")
    for skill, count in skill_counts.most_common(10):
        print(f"  {skill:<25} {count} jobs  ({round(count / updated * 100, 1)}%)")


if __name__ == "__main__":
    process_all_jobs()