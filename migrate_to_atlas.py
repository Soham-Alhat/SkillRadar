from pymongo import MongoClient
import certifi

LOCAL = "mongodb://localhost:27017"

ATLAS = "mongodb+srv://sohamalhat:o7wsStSMKfe7m91w@skillradar.hcuyvcs.mongodb.net/skillradar?retryWrites=true&w=majority&appName=skillradar"

local = MongoClient(LOCAL)["skillradar"]

atlas = MongoClient(
    ATLAS,
    tls=True,
    tlsCAFile=certifi.where()
)["skillradar"]

for col in ["jobs", "skills"]:
    docs = list(local[col].find({}, {"_id": 0}))

    if docs:
        atlas[col].drop()
        atlas[col].insert_many(docs)

        print(f"{col}: {len(docs)} docs migrated")