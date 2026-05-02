import scrapy
import json
from pymongo import MongoClient
from datetime import datetime

APP_ID  = "3b68a26f"
APP_KEY = "2b7cba3c7fd4725ab94d6df94c9e0966"

class JobSpider(scrapy.Spider):
    name = "jobs"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 1,
    }

    def __init__(self):
        super().__init__()
        client = MongoClient("mongodb://localhost:27017")
        self.col = client["skillradar"]["jobs"]

    def start_requests(self):
        roles = [
            "data analyst",
            "python developer",
            "data scientist",
            "machine learning",
            "business analyst"
        ]
        for role in roles:
            url = (
                f"https://api.adzuna.com/v1/api/jobs/in/search/1"
                f"?app_id={APP_ID}&app_key={APP_KEY}"
                f"&results_per_page=50&what={role.replace(' ', '%20')}"
                f"&content-type=application/json"
            )
            yield scrapy.Request(url, callback=self.parse, meta={"role": role})

    def parse(self, response):
        data = json.loads(response.text)
        jobs = data.get("results", [])
        self.logger.info(f"Got {len(jobs)} jobs for: {response.meta['role']}")

        for job in jobs:
            record = {
                "title"      : job.get("title", ""),
                "company"    : job.get("company", {}).get("display_name", ""),
                "location"   : job.get("location", {}).get("display_name", ""),
                "description": job.get("description", "")[:500],
                "role"       : response.meta["role"],
                "source"     : "adzuna",
                "scraped_at" : datetime.utcnow()
            }
            self.col.update_one(
                {"title": record["title"], "company": record["company"]},
                {"$set": record},
                upsert=True
            )
            yield record