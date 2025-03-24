from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.event import listens_for

from app import db


class Base(db.Model):
    """Base model that includes created_at and updated_at timestamps."""

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
    """Update the updated_at timestamp before an update."""
    target.updated_at = datetime.now(timezone.utc)


class User(Base):
    """User model representing a user in the application."""

    __tablename__ = "users"
    user_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))

    # Relationship to UserService
    user_services: so.WriteOnlyMapped["UserService"] = so.relationship(
        "UserService",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<User: {self.username}>"


class Service(Base):
    """Service model representing an external service integrated with the application."""

    __tablename__ = "services"
    service_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    service_name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True
    )
    service_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    # Relationship to UserService
    user_services: so.WriteOnlyMapped["UserService"] = so.relationship(
        "UserService",
        back_populates="service",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Service: {self.service_name}>"


class UserService(Base):
    """UserService model representing the association between users and services."""

    __tablename__ = "user_services"
    user_services_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.user_id, ondelete="CASCADE"), index=True
    )
    service_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Service.service_id, ondelete="CASCADE"), index=True
    )
    access_token: so.Mapped[str] = so.mapped_column(sa.String(256))
    refresh_token: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)
    expires_in: so.Mapped[Optional[int]] = so.mapped_column(nullable=True)

    # Relationships
    user: so.Mapped["User"] = so.relationship("User", back_populates="user_services")
    service: so.Mapped["Service"] = so.relationship(
        "Service", back_populates="user_services"
    )

    def __repr__(self):
        return (
            f"<UserService: user_id={self.user_id}, "
            f"service_id={self.service_id}, "
            f"access_token_present={'Yes' if self.access_token else 'No'}, "
            f"expires_in={self.expires_in}>"
        )
