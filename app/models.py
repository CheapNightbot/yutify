import os
import pickle
import random
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

# ==== OAuth 2.0 Related ====
from authlib.integrations.sqla_oauth2 import (
    OAuth2AuthorizationCodeMixin,
    OAuth2ClientMixin,
    OAuth2TokenMixin,
)

# ===========================
from cryptography.exceptions import InvalidKey
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import current_app
from flask_security.models import fsqla_v3 as fsqla
from sqlalchemy.event import listens_for

from app.extensions import db

load_dotenv()


class Encrypted(sa.TypeDecorator):
    impl = sa.Text
    cache_ok = True

    def __init__(self, encryption_key: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_key = encryption_key or os.environ.get("ENCRYPTION_KEY")
        self.fernet = Fernet(self.encryption_key.encode())

    def process_bind_param(self, value, dialect):
        if value is not None:
            try:
                value = self.fernet.encrypt(pickle.dumps(value)).decode()
            except InvalidKey as e:
                current_app.logger.critical(f"Encryption Error: {e}")
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                value = pickle.loads(self.fernet.decrypt(value.encode()))
            except InvalidKey as e:
                current_app.logger.warning(f"Decryption Error: {e}")
        return value


fsqla.FsModels.set_db_info(
    db, user_table_name="users", role_table_name="roles", webauthn_table_name="webauthn"
)


class Base(db.Model):
    """Base model that includes created_at and updated_at timestamps."""

    __abstract__ = True
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


@listens_for(Base, "before_update", named=True)
def update_timestamps(mapper, connection, target):
    """Update the updated_at timestamp before an update."""
    target.updated_at = datetime.now(timezone.utc)


class Role(db.Model, fsqla.FsRoleMixin):
    """Role model representing a role in the application."""

    __tablename__ = "roles"


class WebAuthn(db.Model, fsqla.FsWebAuthnMixin):
    """WebAuthn model representing web auth information associated with a user."""

    __tablename__ = "webauthn"


class User(db.Model, fsqla.FsUserMixin):
    """User model representing a user in the application."""

    __tablename__ = "users"
    name: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=True)
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=True)
    avatar: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), unique=True, nullable=False
    )
    is_profile_public: so.Mapped[bool] = so.mapped_column(
        sa.Boolean(), server_default=sa.false(), nullable=False
    )
    create_datetime: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    update_datetime: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to UserService: one-to-many
    user_services: so.Mapped[list["UserService"]] = so.relationship(
        "UserService", back_populates="user", cascade="all, delete", uselist=True
    )

    def __repr__(self):
        return f"<User: {self.name}@{self.username}>"

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
            self.avatar = f"icons/{selected_avatar}"

        except Exception as e:
            current_app.logger.warning(f"Error setting avatar: {e}")
            self.avatar = "favicon.svg"  # Fallback if something goes wrong

    def get_user_id(self):
        return self.id


class Service(Base):
    """Service model representing an external service integrated with the application."""

    __tablename__ = "services"
    id: so.Mapped[int] = so.mapped_column(sa.Integer(), primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)
    # Whether this service supports user authentication
    is_private: so.Mapped[bool] = so.mapped_column(sa.Boolean(), default=False)
    access_token: so.Mapped[Optional[str]] = so.mapped_column(
        Encrypted(), nullable=True
    )
    expires_in: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer(), nullable=True)
    requested_at: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Float(), nullable=True
    )

    # Relationship to UserService: one-to-many
    user_services: so.Mapped["UserService"] = so.relationship(
        "UserService",
        back_populates="service",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"<Service: {self.name}@{self.url}>"


class UserService(Base):
    """UserService model representing the association between users and services."""

    __tablename__ = "user_services"
    id: so.Mapped[int] = so.mapped_column(sa.Integer(), primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id, ondelete="CASCADE"), index=True
    )
    service_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Service.id, ondelete="CASCADE"), index=True
    )
    username: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)
    profile_url: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(256), nullable=True
    )
    access_token: so.Mapped[str] = so.mapped_column(Encrypted(), nullable=True)
    refresh_token: so.Mapped[str] = so.mapped_column(Encrypted(), nullable=True)
    expires_in: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer(), nullable=True)
    requested_at: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Float(), nullable=True
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


class UserData(Base):
    """UserData model representing the most recent music metadata for a user's listening activity."""

    __tablename__ = "users_data"
    id: so.Mapped[int] = so.mapped_column(sa.Integer(), primary_key=True)
    user_service_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(UserService.id, ondelete="CASCADE"), unique=True
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
            sa.select(UserData).where(UserData.user_service_id == user_service.id)
        )

        if existing_data:
            existing_data.data = new_data
            so.attributes.flag_modified(existing_data, "data")
            db.session.add(existing_data)
        else:
            new_entry = UserData(
                user_service_id=user_service.id,
                data=new_data,
                user_service=user_service,
            )
            db.session.add(new_entry)

        db.session.commit()

    def __repr__(self):
        return f"<UserData: user_service_id={self.user_service_id}, updated_at={self.updated_at}>"


# ==== OAuth 2.0 Related ====
class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = "oauth2_client"

    id: so.Mapped[int] = so.mapped_column(sa.Integer(), primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id, ondelete="CASCADE"), index=True
    )
    user: so.Mapped["User"] = db.relationship("User")


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = "oauth2_code"

    id: so.Mapped[int] = so.mapped_column(sa.Integer(), primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id, ondelete="CASCADE"), index=True
    )
    user: so.Mapped["User"] = db.relationship("User")


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = "oauth2_token"

    id: so.Mapped[int] = so.mapped_column(sa.Integer(), primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id, ondelete="CASCADE"), index=True
    )
    user: so.Mapped["User"] = db.relationship("User")

    def is_refresh_token_active(self):
        if self.is_revoked():
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time()
