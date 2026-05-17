import os
from supabase import create_client
from datetime import datetime, timezone


def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        try:
            import toml, pathlib
            p = pathlib.Path(__file__).parent / "dashboard" / ".streamlit" / "secrets.toml"
            s = toml.load(p)
            url = s.get("SUPABASE_URL", "")
            key = s.get("SUPABASE_KEY", "")
        except Exception:
            pass
    return create_client(url, key)


class SupabasePipeline:
    def open_spider(self, spider):
        self.supa  = get_supabase()
        self.batch = []

    def close_spider(self, spider):
        if self.batch:
            self.supa.table("jobs").upsert(
                self.batch, on_conflict="title,company"
            ).execute()

    def process_item(self, item, spider):
        self.batch.append(dict(item))
        if len(self.batch) >= 50:
            self.supa.table("jobs").upsert(
                self.batch, on_conflict="title,company"
            ).execute()
            self.batch = []
        return item