import asyncio
import os
import time
from pprint import pprint
from datetime import datetime

from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "geo_users")


async def seed(col):
    await col.drop()
    docs = [
        {
            "external_id": f"u{i}",
            "full_name": name,
            "email": f"{name.split()[0].lower()}@example.com",
            "address": {"city": city, "country_code": country, "street": "Async Avenue"},
            "engagement_score": i * 10,
            "created_at": datetime.utcnow(),
        }
        for i, (name, city, country) in enumerate(
            [
                ("Ivan Petrenko", "Kyiv", "UA"),
                ("Maria Shevchenko", "Lviv", "UA"),
                ("Ola Nowak", "Warsaw", "PL"),
                ("Pablo García", "Madrid", "ES"),
            ],
            start=1,
        )
    ]
    await col.insert_many(docs, ordered=False)
    await col.create_index("external_id", unique=True)
    await col.create_index([("address.country_code", 1), ("engagement_score", -1)])


async def async_queries(col):
    # Паралельні запити для демонстрації неблокуючої роботи
    tasks = [
        col.count_documents({"address.country_code": "UA"}),
        col.find_one({"address.city": "Warsaw"}),
        col.aggregate(
            [
                {"$group": {"_id": "$address.country_code", "avg_score": {"$avg": "$engagement_score"}}},
                {"$sort": {"avg_score": -1}},
            ]
        ).to_list(length=None),
    ]
    return await asyncio.gather(*tasks)


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    col = db.async_users
    await seed(col)

    started = time.perf_counter()
    user_count, warsaw_user, aggregates = await async_queries(col)
    elapsed = time.perf_counter() - started

    print(f"Parallel queries done in {elapsed:.4f}s")
    print("Users in UA (count)", user_count)
    print("Warsaw user:")
    pprint(warsaw_user)
    print("Aggregates:")
    pprint(aggregates)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:  # pragma: no cover
        print("MongoDB is not reachable. Run docker-compose or set MONGO_URI to Atlas.")
        print(exc)
