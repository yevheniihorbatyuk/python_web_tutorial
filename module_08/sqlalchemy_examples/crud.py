from __future__ import annotations

import argparse
from typing import Iterable, List

from sqlalchemy import select

from sqlalchemy_examples.database import get_session
from sqlalchemy_examples.models import Address, City, Country, User


def create_country(name: str, iso_code: str) -> Country:
    with get_session() as session:
        country = Country(name=name, iso_code=iso_code.upper())
        session.add(country)
        session.flush()
        return country


def create_city(name: str, country: Country) -> City:
    with get_session() as session:
        city = City(name=name, country_id=country.id)
        session.add(city)
        session.flush()
        return city


def create_user(full_name: str, email: str, address: Address) -> User:
    with get_session() as session:
        user = User(full_name=full_name, email=email, address_id=address.id)
        session.add(user)
        session.flush()
        return user


def find_cities_by_country(iso_code: str) -> List[str]:
    with get_session() as session:
        stmt = (
            select(City.name)
            .join(Country)
            .where(Country.iso_code == iso_code.upper())
            .order_by(City.name)
        )
        rows: Iterable[tuple[str]] = session.execute(stmt).all()
        return [name for (name,) in rows]


def find_users_in_country(iso_code: str) -> List[str]:
    with get_session() as session:
        stmt = (
            select(User.full_name)
            .join(Address)
            .join(City)
            .join(Country)
            .where(Country.iso_code == iso_code.upper(), User.is_active.is_(True))
            .order_by(User.full_name)
        )
        rows: Iterable[tuple[str]] = session.execute(stmt).all()
        return [name for (name,) in rows]


def soft_delete_user(email: str) -> None:
    with get_session() as session:
        user: User | None = session.scalar(select(User).where(User.email == email))
        if user:
            user.is_active = False


def demo_queries() -> None:
    print("Cities in UA:", find_cities_by_country("UA"))
    print("Users in UA:", find_users_in_country("UA"))
    soft_delete_user("maria@example.com")
    print("Users in UA after soft delete:", find_users_in_country("UA"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLAlchemy CRUD demo")
    parser.add_argument("--country", help="ISO code to list cities", default=None)
    parser.add_argument("--users-in", dest="users_in", help="ISO code to list users", default=None)
    parser.add_argument("--demo", action="store_true", help="Run quick demo queries")
    args = parser.parse_args()

    if args.demo:
        demo_queries()
    if args.country:
        print(find_cities_by_country(args.country))
    if args.users_in:
        print(find_users_in_country(args.users_in))
