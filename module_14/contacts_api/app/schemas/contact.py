from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    """Partial update — every field is optional."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    birthday: Optional[date]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
