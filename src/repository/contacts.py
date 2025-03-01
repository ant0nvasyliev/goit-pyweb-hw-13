from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.entity.models import Contact, User

from src.schemas.contact import ContactSchema, ContactUpdate


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_by_id(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    try:
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists."
        )


async def update_contact(contact_id: int, body: ContactUpdate, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        return None
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if not contact:
        return None
    await db.delete(contact)
    await db.commit()
    return contact


async def search_contacts(query: str, db: AsyncSession, user: User):
    stmt = select(Contact).where(
        or_(
            Contact.first_name.ilike(f"%{query}%"),
            Contact.second_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%"),
        ), user=user
    )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_upcoming_birthdays(db: AsyncSession, user: User):
    today = date.today()
    next_week = today + timedelta(days=7)
    stmt = select(Contact).where(
        Contact.birth_date.between(today, next_week), user=user
    )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()
