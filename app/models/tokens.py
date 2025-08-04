from sqlalchemy import BigInteger, ForeignKey, DateTime, CheckConstraint, String, Float, Text, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from uuid import uuid4

from typing import TYPE_CHECKING, Optional

from app.models.base import Base

class RefreshTokenModel(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid4().hex) 
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    expires_at: Mapped[datetime]
    is_used: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
