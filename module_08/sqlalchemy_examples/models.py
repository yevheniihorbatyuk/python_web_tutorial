from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    iso_code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False, index=True)
    cities: Mapped[List["City"]] = relationship(back_populates="country", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Country({self.iso_code})"


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"))
    country: Mapped[Country] = relationship(back_populates="cities")
    addresses: Mapped[List["Address"]] = relationship(back_populates="city", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"City({self.name})"


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    street: Mapped[str] = mapped_column(String(200), nullable=False)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    city: Mapped[City] = relationship(back_populates="addresses")
    users: Mapped[List["User"]] = relationship(back_populates="address")

    def __repr__(self) -> str:
        return f"Address({self.street})"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    address: Mapped[Address] = relationship(back_populates="users")

    def __repr__(self) -> str:
        return f"User({self.email})"
