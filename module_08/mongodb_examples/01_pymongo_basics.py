import os
from pprint import pprint
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "geo_users")


def bootstrap_collection(db):
    users = db.users
    users.drop()
    docs = [
        {
            "external_id": "u1",
            "full_name": "Ivan Petrenko",
            "email": "ivan@example.com",
            "address": {"city": "Kyiv", "country_code": "UA", "street": "Main Street"},
            "interests": ["ml", "gis"],
            "created_at": datetime.utcnow(),
        },
        {
            "external_id": "u2",
            "full_name": "Maria Shevchenko",
            "email": "maria@example.com",
            "address": {"city": "Lviv", "country_code": "UA", "street": "Shevchenka Ave"},
            "interests": ["analytics"],
            "created_at": datetime.utcnow(),
        },
        {
            "external_id": "u3",
            "full_name": "Ola Nowak",
            "email": "ola@example.com",
            "address": {"city": "Warsaw", "country_code": "PL", "street": "Marszalkowska"},
            "interests": ["data eng", "streaming"],
            "created_at": datetime.utcnow(),
        },
    ]
    users.insert_many(docs)
    users.create_index("external_id", unique=True)
    users.create_index([("address.country_code", 1), ("address.city", 1)])
    return users


def find_cities_by_country(users):
    pipeline = [
        {"$group": {"_id": "$address.country_code", "cities": {"$addToSet": "$address.city"}}},
        {"$sort": {"_id": 1}},
    ]
    return list(users.aggregate(pipeline))


def find_users_in_country(users, country_code: str):
    cursor = users.find({"address.country_code": country_code.upper()}).sort("full_name", 1)
    return list(cursor)


def upsert_user(users, payload: dict):
    users.update_one({"external_id": payload["external_id"]}, {"$set": payload}, upsert=True)


def main():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    users = bootstrap_collection(db)

    print("Cities grouped by country code:")
    pprint(find_cities_by_country(users))

    print("\nUsers in UA:")
    pprint(find_users_in_country(users, "UA"))

    print("\nUpserting user from RabbitMQ-like event:")
    upsert_user(
        users,
        {
            "external_id": "u3",
            "full_name": "Ola Nowak",
            "email": "ola@example.com",
            "address": {"city": "Warsaw", "country_code": "PL", "street": "Renovated 2024"},
            "interests": ["data eng", "streaming", "cdc"],
            "updated_at": datetime.utcnow(),
        },
    )
    pprint(users.find_one({"external_id": "u3"}))

    print("\nTop 2 newest users:")
    pprint(list(users.find({}, limit=2).sort("created_at", DESCENDING)))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - демонстраційний хендлер
        print("MongoDB is not reachable. Start docker-compose or point MONGO_URI to Atlas.")
        print(exc)
