from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class UserRole(enum.Enum):
    GUEST = "guest"
    ATHLETE = "athlete"
    COACH = "coach"
    SCHOOL_REP = "school_rep"
    SECRETARY = "secretary"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    athlete_profile: Mapped[Optional["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="user", uselist=False
    )
    coach_profile: Mapped[Optional["CoachProfile"]] = relationship(
        "CoachProfile", back_populates="user", uselist=False
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(
        String(500), unique=True, nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)

    # НОВЫЕ ПОЛЯ
    founder: Mapped[str] = mapped_column(String(200), nullable=True)  # Основатель
    founded_year: Mapped[int] = mapped_column(Integer, nullable=True)  # Год основания
    city: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)  # Нынешний адрес
    phone: Mapped[str] = mapped_column(String(20), nullable=True)


    email: Mapped[str] = mapped_column(String(100), nullable=True)
    # Социальные сети
    vk_url: Mapped[str] = mapped_column(String(200), nullable=True)
    telegram_url: Mapped[str] = mapped_column(String(200), nullable=True)
    youtube_url: Mapped[str] = mapped_column(String(200), nullable=True)
    instagram_url: Mapped[str] = mapped_column(String(200), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)


    email: Mapped[str] = mapped_column(String(100), nullable=True)
    website: Mapped[str] = mapped_column(String(200), nullable=True)
    # Социальные сети
    vk_url: Mapped[str] = mapped_column(String(200), nullable=True)
    telegram_url: Mapped[str] = mapped_column(String(200), nullable=True)
    youtube_url: Mapped[str] = mapped_column(String(200), nullable=True)
    instagram_url: Mapped[str] = mapped_column(String(200), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)



    # ИЗОБРАЖЕНИЯ
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)  # Логотип
    cover_url: Mapped[str] = mapped_column(String(500), nullable=True)  # Обложка школы

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    branches: Mapped[list["Branch"]] = relationship(
        "Branch", back_populates="school", cascade="all, delete-orphan"
    )
    athletes: Mapped[list["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="school"
    )
    coaches: Mapped[list["CoachProfile"]] = relationship(
        "CoachProfile", back_populates="school"
    )


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)


    email: Mapped[str] = mapped_column(String(100), nullable=True)
    # Социальные сети
    vk_url: Mapped[str] = mapped_column(String(200), nullable=True)
    telegram_url: Mapped[str] = mapped_column(String(200), nullable=True)
    youtube_url: Mapped[str] = mapped_column(String(200), nullable=True)
    instagram_url: Mapped[str] = mapped_column(String(200), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)



    # НОВОЕ ПОЛЕ - обложка филиала (если нет - берется от школы)
    cover_url: Mapped[str] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    school: Mapped["School"] = relationship("School", back_populates="branches")
    athletes: Mapped[list["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="branch"
    )
    coaches: Mapped[list["CoachProfile"]] = relationship(
        "CoachProfile", back_populates="branch"
    )


class CoachProfile(Base):
    __tablename__ = "coach_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    school_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schools.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ИЗОБРАЖЕНИЯ
    photo_url: Mapped[str] = mapped_column(String(500), nullable=True)  # Аватар тренера
    cover_url: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # Обложка (берется от школы если не указана)

    bio: Mapped[str] = mapped_column(String(1000), nullable=True)
    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    qualification: Mapped[str] = mapped_column(String(100), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    specialization: Mapped[str] = mapped_column(String(200), nullable=True)
    is_head_coach: Mapped[bool] = mapped_column(Boolean, default=False)
    achievements: Mapped[str] = mapped_column(String(1000), nullable=True)
    # Социальные сети
    vk_url: Mapped[str] = mapped_column(String(200), nullable=True)
    telegram_url: Mapped[str] = mapped_column(String(200), nullable=True)
    youtube_url: Mapped[str] = mapped_column(String(200), nullable=True)
    instagram_url: Mapped[str] = mapped_column(String(200), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(100), nullable=True)



    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="coach_profile")
    school: Mapped[Optional["School"]] = relationship(
        "School", back_populates="coaches"
    )
    branch: Mapped[Optional["Branch"]] = relationship(
        "Branch", back_populates="coaches"
    )
    athletes: Mapped[list["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="coach"
    )


class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    school_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("schools.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    coach_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("coach_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ИЗОБРАЖЕНИЯ
    photo_url: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # Аватар спортсмена
    cover_url: Mapped[str] = mapped_column(
        String(500), nullable=True
    )  # Обложка (берется от школы если не указана)

    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=True, index=True)
    rank: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="athlete_profile")
    school: Mapped[Optional["School"]] = relationship(
        "School", back_populates="athletes"
    )
    branch: Mapped[Optional["Branch"]] = relationship(
        "Branch", back_populates="athletes"
    )
    coach: Mapped[Optional["CoachProfile"]] = relationship(
        "CoachProfile", back_populates="athletes"
    )
    personal_bests: Mapped[list["PersonalBest"]] = relationship(
        "PersonalBest", back_populates="athlete", cascade="all, delete-orphan"
    )
    entries: Mapped[list["Entry"]] = relationship(
        "Entry", back_populates="athlete", cascade="all, delete-orphan"
    )


class PersonalBest(Base):
    __tablename__ = "personal_bests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    athlete_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("athlete_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    distance: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 50, 100, 200, 400, 800, 1500
    stroke: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # freestyle, breaststroke, backstroke, butterfly
    time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    set_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    athlete: Mapped["AthleteProfile"] = relationship(
        "AthleteProfile", back_populates="personal_bests"
    )


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    venue: Mapped[str] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    max_participants: Mapped[int] = mapped_column(Integer, default=0)

    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи (пока закомментируем, добавим позже)
    age_categories: Mapped[list["AgeCategory"]] = relationship(
        "AgeCategory", back_populates="competition", cascade="all, delete-orphan"
    )
    swim_events: Mapped[list["SwimEvent"]] = relationship(
        "SwimEvent", back_populates="competition", cascade="all, delete-orphan"
    )
    entries: Mapped[list["Entry"]] = relationship(
        "Entry", back_populates="competition", cascade="all, delete-orphan"
    )
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])


class AgeCategory(Base):
    __tablename__ = "age_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "10-12 лет", "13-15 лет"
    min_age: Mapped[int] = mapped_column(Integer, nullable=False)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(
        String(10), nullable=True
    )  # male, female, mixed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связь с соревнованием
    competition: Mapped["Competition"] = relationship(
        "Competition", back_populates="age_categories"
    )


class SwimEvent(Base):
    __tablename__ = "swim_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # "50m Freestyle"
    distance: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 50, 100, 200, 400, 800, 1500
    stroke: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # freestyle, breaststroke, backstroke, butterfly, medley
    gender: Mapped[str] = mapped_column(
        String(10), nullable=True
    )  # male, female, mixed
    is_relay: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)  # порядок проведения
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    competition: Mapped["Competition"] = relationship(
        "Competition", back_populates="swim_events"
    )
    entries: Mapped[list["Entry"]] = relationship(
        "Entry", back_populates="swim_event", cascade="all, delete-orphan"
    )
    heats: Mapped[list["Heat"]] = relationship(
        "Heat", back_populates="swim_event", cascade="all, delete-orphan"
    )


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    competition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    swim_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("swim_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    athlete_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("athlete_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, confirmed, rejected, scratched
    entry_time: Mapped[float] = mapped_column(
        Float, nullable=True
    )  # заявленное время (сек)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    competition: Mapped["Competition"] = relationship(
        "Competition", back_populates="entries"
    )
    swim_event: Mapped["SwimEvent"] = relationship(
        "SwimEvent", back_populates="entries"
    )
    athlete: Mapped["AthleteProfile"] = relationship(
        "AthleteProfile", back_populates="entries"
    )
    heat_entry: Mapped[Optional["HeatEntry"]] = relationship(
        "HeatEntry", back_populates="entry", uselist=False
    )


class Heat(Base):
    __tablename__ = "heats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    swim_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("swim_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    heat_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lane_count: Mapped[int] = mapped_column(Integer, default=8)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    swim_event: Mapped["SwimEvent"] = relationship("SwimEvent", back_populates="heats")
    entries: Mapped[list["HeatEntry"]] = relationship(
        "HeatEntry", back_populates="heat", cascade="all, delete-orphan"
    )


class HeatEntry(Base):
    __tablename__ = "heat_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    heat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("heats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entries.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    lane: Mapped[int] = mapped_column(Integer, nullable=False)
    result_time: Mapped[float] = mapped_column(Float, nullable=True)
    place: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связи
    heat: Mapped["Heat"] = relationship("Heat", back_populates="entries")
    entry: Mapped["Entry"] = relationship("Entry", back_populates="heat_entry")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # competition_1 или support
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", backref="chat_messages")


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Связи
    author: Mapped[Optional["User"]] = relationship("User", backref="news")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(10000), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # technique, nutrition, rules, etc.
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True
    )
    views: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Связи
    author: Mapped[Optional["User"]] = relationship("User", backref="articles")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", backref="password_reset_tokens")
