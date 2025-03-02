from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, ForeignKey, func, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    second_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    birth_date: Mapped[str] = mapped_column(Date, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now(),
                                                 nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")




class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, index=True, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    avatar: Mapped[str] = mapped_column(String(250), nullable=True, index=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)