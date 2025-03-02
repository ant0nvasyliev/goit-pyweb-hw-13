from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdate, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=20), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_db),
                            user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contact_by_id(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}', response_model=ContactResponse)
async def update_contact(
        contact_id: int = Path(..., ge=1),
        body: ContactUpdate = Depends(),
        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact


@router.delete('/{contact_id}', response_model=dict)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return {"message": "Deleted successfully"}


@router.get('/search/', response_model=list[ContactResponse])
async def search_contacts(query: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.search_contacts(query, db, user)
    return contacts


@router.get('/birthdays/', response_model=list[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_upcoming_birthdays(db, user)
    return contacts
