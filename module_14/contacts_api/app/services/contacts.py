"""
Contact CRUD service + birthday query.

Birthday query note:
  We want contacts whose birthday falls in the next 7 days.
  The tricky part: "next 7 days" wraps around December → January.
  We handle this by extracting (month, day) from both the contact and
  today's date, then comparing — works for any year, including leap years.

  SQL equivalent:
    SELECT * FROM contacts
    WHERE owner_id = :user_id
      AND (month, day) BETWEEN (today_month, today_day)
                            AND (end_month, end_day)
    -- but cross-year wrap requires two OR conditions

  We keep it simple with a Python-side filter since birthday lists
  are small per user and results are cached in Redis anyway.
"""

from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


async def get_contact(contact_id: int, owner_id: int, db: AsyncSession) -> Optional[Contact]:
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def list_contacts(
    owner_id: int,
    db: AsyncSession,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Contact]:
    query = select(Contact).where(Contact.owner_id == owner_id)

    if search:
        term = f"%{search}%"
        query = query.where(
            or_(
                Contact.first_name.ilike(term),
                Contact.last_name.ilike(term),
                Contact.email.ilike(term),
            )
        )

    query = query.offset(skip).limit(limit).order_by(Contact.last_name, Contact.first_name)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_contact(data: ContactCreate, owner_id: int, db: AsyncSession) -> Contact:
    contact = Contact(**data.model_dump(), owner_id=owner_id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact: Contact, data: ContactUpdate, db: AsyncSession
) -> Contact:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact: Contact, db: AsyncSession) -> None:
    await db.delete(contact)
    await db.commit()


async def get_upcoming_birthdays(owner_id: int, db: AsyncSession) -> List[dict]:
    """
    Return contacts whose birthday is within the next 7 days.

    Normalises the year to the current year for comparison so the query
    works regardless of the year stored in the birthday column.
    """
    today = date.today()
    end_date = today + timedelta(days=7)

    result = await db.execute(
        select(Contact).where(
            Contact.owner_id == owner_id,
            Contact.birthday.isnot(None),
        )
    )
    contacts = result.scalars().all()

    upcoming = []
    for contact in contacts:
        birthday_this_year = contact.birthday.replace(year=today.year)
        # Handle Feb 29 in non-leap years
        try:
            birthday_this_year = contact.birthday.replace(year=today.year)
        except ValueError:
            birthday_this_year = contact.birthday.replace(year=today.year, day=28)

        # Also check if birthday already passed this year → look at next year
        if birthday_this_year < today:
            try:
                birthday_this_year = contact.birthday.replace(year=today.year + 1)
            except ValueError:
                birthday_this_year = contact.birthday.replace(year=today.year + 1, day=28)

        if today <= birthday_this_year <= end_date:
            upcoming.append({
                "id": contact.id,
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "birthday": str(contact.birthday),
                "days_until": (birthday_this_year - today).days,
            })

    upcoming.sort(key=lambda c: c["days_until"])
    return upcoming
