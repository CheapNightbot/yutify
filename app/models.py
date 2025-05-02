import hashlib
import os
import random
from datetime import datetime, timezone
from pathlib import Path
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
    _avatar: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    _email: so.Mapped[str] = so.mapped_column(sa.String(128), unique=True)
    _email_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), index=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    # Relationship to UserService: one-to-many
    user_services: so.Mapped[list["UserService"]] = so.relationship(
        "UserService", back_populates="user", cascade="all, delete", uselist=True
    )

    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    @property
    def avatar(self):
        return self._avatar

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

    def set_avatar(self):
        """Set a random avatar from the available icons in the static folder."""
        icons_folder = Path(current_app.static_folder) / "icons"
        try:
            # Get all valid image files from the icons folder
            valid_extensions = {".png", ".jpg", ".jpeg", ".svg"}
            available_avatars = [
                file.name
                for file in icons_folder.iterdir()
                if file.is_file() and file.suffix.lower() in valid_extensions
            ]

            if not available_avatars:
                raise FileNotFoundError("No valid avatars found in the icons folder.")

            # Randomly select an avatar
            selected_avatar = random.choice(available_avatars)

            # Set the avatar property (store only the relative path)
            self._avatar = f"icons/{selected_avatar}"

        except Exception as e:
            current_app.logger.error(f"Error setting avatar: {e}")
            self._avatar = None  # Fallback if something goes wrong

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
    is_private: so.Mapped[bool] = so.mapped_column(
        default=False
    )  # Whether supports user authentication
    _access_token: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)
    expires_in: so.Mapped[Optional[int]] = so.mapped_column(nullable=True)
    requested_at: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)

    # Relationship to UserService: one-to-many
    user_services: so.Mapped["UserService"] = so.relationship(
        "UserService",
        back_populates="service",
        cascade="all, delete",
    )

    @property
    def access_token(self):
        return self.decrypt(self._access_token)

    @access_token.setter
    def access_token(self, value):
        self._access_token = self.encrypt(value)

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
    _access_token: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)
    _refresh_token: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)
    expires_in: so.Mapped[Optional[int]] = so.mapped_column(nullable=True)
    requested_at: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    username: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=True)
    profile_url: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(64), nullable=True
    )

    __table_args__ = (
        sa.UniqueConstraint("user_id", "service_id", name="uq_user_service"),
    )

    # Relationships: many-to-one
    user: so.Mapped["User"] = so.relationship("User", back_populates="user_services")
    service: so.Mapped["Service"] = so.relationship(
        "Service", back_populates="user_services"
    )

    # Relationship to UserData: one-to-one
    user_data: so.Mapped["UserData"] = so.relationship(
        "UserData", back_populates="user_service", cascade="all, delete", uselist=False
    )

    def __repr__(self):
        return (
            f"<UserService: user_id={self.user_id}, "
            f"service_id={self.service_id}, "
            f"username={self.username}, "
            f"access_token_present={'Yes' if self.access_token else 'No'}, "
            f"refresh_token_present={'Yes' if self.refresh_token else 'No'}, "
            f"expires_in={self.expires_in}>"
            f"requested_at={self.requested_at}>"
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

    @staticmethod
    def insert_or_update_user_data(user_service, new_data):
        """Insert or update user data for a given user_service_id."""

        existing_data = db.session.scalar(
            sa.select(UserData).where(
                UserData.user_service_id == user_service.user_services_id
            )
        )

        if existing_data:
            existing_data.data = new_data
            so.attributes.flag_modified(existing_data, "data")
            db.session.add(existing_data)
        else:
            new_entry = UserData(
                user_service_id=user_service.user_services_id,
                data=new_data,
                user_service=user_service,
            )
            db.session.add(new_entry)

        db.session.commit()

    def __repr__(self):
        return f"<UserData: user_service_id={self.user_service_id}, updated_at={self.updated_at}>"
