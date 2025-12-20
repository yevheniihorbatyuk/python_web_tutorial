from __future__ import annotations

from sqlalchemy import text

from sqlalchemy_examples.database import engine, get_session
from sqlalchemy_examples.models import Address, Base, City, Country, User


COUNTRIES = [
    {"name": "Ukraine", "iso_code": "UA"},
    {"name": "Poland", "iso_code": "PL"},
]

CITIES = {
    "UA": ["Kyiv", "Lviv", "Odesa"],
    "PL": ["Warsaw", "Krakow"],
}

USERS = [
    {"full_name": "Ivan Petrenko", "email": "ivan@example.com", "city": "Kyiv"},
    {"full_name": "Maria Shevchenko", "email": "maria@example.com", "city": "Lviv"},
    {"full_name": "Ola Nowak", "email": "ola@example.com", "city": "Warsaw"},
]


def reset_schema() -> None:
    # Danger: drops all tables created by this Base
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def seed() -> None:
    reset_schema()
    with get_session() as session:
        countries = {}
        for country_data in COUNTRIES:
            country = Country(**country_data)
            session.add(country)
            session.flush()
            countries[country.iso_code] = country

        cities = {}
        for iso, names in CITIES.items():
            for name in names:
                city = City(name=name, country=countries[iso])
                session.add(city)
                session.flush()
                cities[name] = city

        for user_data in USERS:
            city = cities[user_data["city"]]
            address = Address(street="Main Street", postal_code="01001", city=city)
            session.add(address)
            session.flush()

            user = User(full_name=user_data["full_name"], email=user_data["email"], address=address)
            session.add(user)

    print("Seed complete. Countries:", list(CITIES.keys()))


if __name__ == "__main__":
    seed()
