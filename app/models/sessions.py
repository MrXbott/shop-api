from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from uuid import uuid4

from app.models.base import Base


class SessionModel(Base):
    __tablename__ = 'sessions'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid4().hex)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user_agent: Mapped[str] = mapped_column(String, nullable=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    last_seen_at: Mapped[datetime] = mapped_column(default=datetime.now)
    expires_at: Mapped[datetime]
    is_active: Mapped[bool] = mapped_column(default=True)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
