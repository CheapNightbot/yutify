import hashlib
import os
from datetime import datetime, timezone
from time import time
from typing import Optional

import jwt
import sqlalchemy as sa
import sqlalchemy.orm as so
from cryptography.exceptions import InvalidKey
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.event import listens_for
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

load_dotenv()

key = os.environ.get("ENCRYPTION_KEY", "potatoes").encode()
cipher = Fernet(key)


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

    @staticmethod
    def encrypt(data: str):
        if not data:
            return None

        try:
            return cipher.encrypt(data.encode())
        except InvalidKey as e:
            print(f"Encryption error: {e}")
            return None

    @staticmethod
    def decrypt(data: str):
        if not data:
            return None

        try:
            return cipher.decrypt(data).decode()
        except InvalidKey as e:
            print(f"Decryption error: {e}")
            return None


@listens_for(Base, "before_update", named=True)
def update_timestamps(mapper, connection, target):
    """Update the updated_at timestamp before an update."""
    target.updated_at = datetime.now(timezone.utc)


class User(UserMixin, Base):
    """User model representing a user in the application."""

    __tablename__ = "users"
    user_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64))
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    _email: so.Mapped[str] = so.mapped_column(sa.String(128), unique=True)
    _email_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), index=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    # Relationship to UserService: one-to-many
    user_services: so.WriteOnlyMapped["UserService"] = so.relationship(
        "UserService",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    @property
    def email(self):
        return self.decrypt(self._email)

    @property
    def email_hash(self):
        return self._email_hash

    @email.setter
    def email(self, value):
        self._email_hash = self.hash_email(value)
        self._email = self.encrypt(value)

    def __repr__(self):
        return f"<User: {self.name}@{self.username}>"

    def get_id(self):
        return str(self.user_id)

    @staticmethod
    def hash_email(email):
        return hashlib.sha256(email.encode()).hexdigest()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.user_id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except Exception:
            return
        return db.session.get(User, user_id)


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Service(Base):
    """Service model representing an external service integrated with the application."""

    __tablename__ = "services"
    service_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    service_name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True
    )
    service_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    # Relationship to UserService: one-to-many
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
    _access_token: so.Mapped[str] = so.mapped_column(sa.String(256))
    _refresh_token: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)
    expires_in: so.Mapped[Optional[int]] = so.mapped_column(nullable=True)
    requested_at: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)

    # Relationships: many-to-one
    user: so.Mapped["User"] = so.relationship("User", back_populates="user_services")
    service: so.Mapped["Service"] = so.relationship(
        "Service", back_populates="user_services"
    )

    # Relationship to UserData: one-to-one
    user_data: so.Mapped["UserData"] = so.relationship(
        "UserData",
        back_populates="user_service",
        cascade="all, delete",
        passive_deletes=True,
        uselist=False,  # Ensures one-to-one relationship
    )

    @property
    def access_token(self):
        return self.decrypt(self._access_token)

    @access_token.setter
    def access_token(self, value):
        self._access_token = self.encrypt(value)

    @property
    def refresh_token(self):
        return self.decrypt(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value):
        self._refresh_token = self.encrypt(value)

    def __repr__(self):
        return (
            f"<UserService: user_id={self.user_id}, "
            f"service_id={self.service_id}, "
            f"access_token_present={'Yes' if self.access_token else 'No'}, "
            f"expires_in={self.expires_in}>"
        )


class UserData(Base):
    """UserData model representing the most recent music metadata for a user's listening activity."""

    __tablename__ = "users_data"
    user_data_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_service_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(UserService.user_services_id, ondelete="CASCADE"), unique=True
    )
    data: so.Mapped[dict] = so.mapped_column(sa.JSON)

    # Relationship to UserService: one-to-one
    user_service: so.Mapped["UserService"] = so.relationship(
        "UserService", back_populates="user_data", uselist=False
    )

    def __repr__(self):
        return f"<UserData: user_service_id={self.user_service_id}, updated_at={self.updated_at}>"
