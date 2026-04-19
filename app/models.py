from sqlalchemy import String, Integer, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import datetime
import enum


class UserRole(enum.Enum):
    GUEST = "guest"
    ATHLETE = "athlete"
    COACH = "coach"
    SCHOOL_REP = "school_rep"
    SECRETARY = "secretary"
    ADMIN = "admin"

    def to_db_value(self) -> str:
        """Преобразует значение для БД (заглавными буквами)"""
        return self.name  # GUEST, ATHLETE, COACH, ...

    @classmethod
    def from_db_value(cls, db_value: str):
        """Преобразует из БД в Python Enum"""
        return cls[db_value]  # ATHLETE → UserRole.ATHLETE


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.GUEST)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
