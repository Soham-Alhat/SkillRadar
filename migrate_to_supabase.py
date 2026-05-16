from pymongo import MongoClient
from supabase import create_client
from datetime import datetime

SUPABASE_URL = "https://dfcovzibvsnfvgonnstv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRmY292emlidnNuZnZnb25uc3R2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MTc4NTksImV4cCI6MjA5NDQ5Mzg1OX0.C23cv_FKRrStdXaU3TY84yg4Wr7hvxiKGyoPKuqevWk"

mongo  = MongoClient("mongodb://localhost:27017")["skillradar"]
supa   = create_client(SUPABASE_URL, SUPABASE_KEY)

# migrate skills
print("Migrating skills...")
skills = list(mongo["skills"].find({}, {"_id": 0}))
if skills:
    supa.table("skills").delete().neq("id", 0).execute()
    for skill in skills:
        supa.table("skills").insert({
            "skill"      : skill.get("skill", ""),
            "count"      : int(skill.get("count", 0)),
            "percentage" : float(skill.get("percentage", 0)),
            "updated_at" : str(datetime.now())
        }).execute()
    print(f"Skills migrated: {len(skills)}")

# migrate jobs
print("Migrating jobs...")
jobs = list(mongo["jobs"].find({}, {
    "_id": 0, "title": 1, "company": 1,
    "role": 1, "location": 1, "extracted_skills": 1
}))
if jobs:
    supa.table("jobs").delete().neq("id", 0).execute()
    batch = []
    for job in jobs:
        batch.append({
            "title"           : job.get("title", ""),
            "company"         : job.get("company", ""),
            "role"            : job.get("role", ""),
            "location"        : job.get("location", ""),
            "extracted_skills": job.get("extracted_skills", []),
            "source"          : "adzuna",
            "scraped_at"      : str(datetime.now())
        })
        if len(batch) == 50:
            supa.table("jobs").insert(batch).execute()
            batch = []
    if batch:
        supa.table("jobs").insert(batch).execute()
    print(f"Jobs migrated: {len(jobs)}")

print("Migration complete.")