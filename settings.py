BOT_NAME = "skillradar"

SPIDER_MODULES = ["spiders"]
NEWSPIDER_MODULE = "spiders"

# Respect robots.txt — set False only for practice/portfolio
ROBOTSTXT_OBEY = False

# Slow down requests so Naukri doesn't block you
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# Browser-like headers to avoid being blocked
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Pipeline to save to MongoDB
ITEM_PIPELINES = {
    "pipelines.SupabasePipeline": 300,
}

# do we have to remove this lines?  

# MONGO_URI = "mongodb://localhost:27017"
# MONGO_DB  = "skillradar"