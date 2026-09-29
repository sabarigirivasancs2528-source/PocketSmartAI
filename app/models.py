from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    Float
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .db import Base


def now():

    return datetime.now(timezone.utc)


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(120)
    )

    password_hash: Mapped[str] = mapped_column(
        String(512)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now
    )


class Recommendation(Base):

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    planner_type: Mapped[str] = mapped_column(
        String(30)
    )

    budget: Mapped[float] = mapped_column(
        Float
    )

    request_json: Mapped[str] = mapped_column(
        Text
    )

    result_json: Mapped[str] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now
    )