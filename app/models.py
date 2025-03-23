from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.event import listens_for

from app import db


class Base(db.Model):
    __abstract__ = True
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


@listens_for(Base, "before_update", named=True)
def update_timestamps(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    user_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))

    def __repr__(self):
        return f"<User {self.username}>"
