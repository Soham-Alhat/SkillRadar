from pymongo import MongoClient
from datetime import datetime


class MongoDBPipeline:

    def open_spider(self, spider):
        self.client = MongoClient("mongodb://localhost:27017")
        self.db     = self.client["skillradar"]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # avoid duplicates by title + company
        self.db["jobs"].update_one(
            {
                "title"  : item.get("title"),
                "company": item.get("company")
            },
            {"$set": dict(item)},
            upsert=True
        )
        return item