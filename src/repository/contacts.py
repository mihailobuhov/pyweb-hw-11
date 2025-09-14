from sqlalchemy import select, and_, extract, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact
from src.schemas.contact import ContactCreateSchema, ContactUpdateSchema
from datetime import date, timedelta

async def get_contacts(limit: int, offset: int, first_name: str, last_name: str,
                       email: str, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    if first_name or last_name or email:
        stmt = stmt.filter(
            and_(
                first_name is None or Contact.first_name.ilike(
                    f"%{first_name}%"),
                last_name is None or Contact.last_name.ilike(f"%{last_name}%"),
                email is None or Contact.email.ilike(f"%{email}%"),
            )
        )
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactCreateSchema, db: AsyncSession):
    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema,
                         db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)
        await db.commit()
        await db.refresh(contact)
        print("Contact updated")
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_upcoming_birthdays(db: AsyncSession):
    try:
        today = date.today()
        end_date = today + timedelta(days=7)

        # Обробка дат у форматі MM-DD для врахування місяця та дня
        stmt = select(Contact).filter(
            and_(
                func.to_char(Contact.birthday, 'MM-DD') >= func.to_char(today, 'MM-DD'),
                func.to_char(Contact.birthday, 'MM-DD') <= func.to_char(end_date, 'MM-DD')
            )
        )
        result = await db.execute(stmt)
        contacts = result.scalars().all()
        print(f"Contacts fetched: {contacts}")  # Логування отриманих контактів
        return contacts
    except Exception as e:
        print("Error fetching upcoming birthdays:", e)  # Логування помилки
        raise Exception(f"Error fetching upcoming birthdays: {e}")
