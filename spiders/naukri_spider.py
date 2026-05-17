import scrapy
import json
import os
from supabase import create_client
from datetime import datetime, timezone


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
    return create_client(url, key)

APP_ID  = os.environ.get("ADZUNA_APP_ID",  "3b68a26f")
APP_KEY = os.environ.get("ADZUNA_APP_KEY", "2b7cba3c7fd4725ab94d6df94c9e0966")


class JobSpider(scrapy.Spider):
    name = "jobs"

    custom_settings = {
        "ROBOTSTXT_OBEY" : False,
        "DOWNLOAD_DELAY" : 1,
    }

    def __init__(self):
        super().__init__()
        self.supa = get_supabase()

    def start_requests(self):
        roles = [
            "data analyst",
            "python developer",
            "data scientist",
            "machine learning engineer",
            "business analyst",
            "data engineer",
            "sql developer",
            "power bi developer"
        ]
        for role in roles:
            for page in range(1, 4):
                url = (
                    f"https://api.adzuna.com/v1/api/jobs/in/search/{page}"
                    f"?app_id={APP_ID}&app_key={APP_KEY}"
                    f"&results_per_page=50&what={role.replace(' ', '%20')}"
                    f"&content-type=application/json"
                )
                yield scrapy.Request(url, callback=self.parse, meta={"role": role})

    def parse(self, response):          # ← 4 spaces indent, inside the class
        try:
            data = json.loads(response.text)
        except Exception:
            return

        jobs = data.get("results", [])
        self.logger.info(f"Got {len(jobs)} jobs for: {response.meta['role']}")

        seen  = set()
        batch = []
        for job in jobs:
            title   = job.get("title", "").strip()
            company = job.get("company", {}).get("display_name", "").strip()
            key     = (title.lower(), company.lower())

            if key in seen or not title:
                continue
            seen.add(key)

            batch.append({
                "title"      : title,
                "company"    : company,
                "location"   : job.get("location", {}).get("display_name", ""),
                "description": job.get("description", ""),
                "role"       : response.meta["role"],
                "source"     : "adzuna",
                "scraped_at" : str(datetime.now(timezone.utc))
            })

        if batch:
            try:
                self.supa.table("jobs").upsert(
                    batch,
                    on_conflict="title,company"
                ).execute()
            except Exception as e:
                self.logger.error(f"Supabase insert failed: {e}")