from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from datetime import datetime
from uuid import uuid4


from app.models.base import Base

class RefreshTokenModel(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid4().hex) 
    session_id: Mapped[str] = mapped_column(ForeignKey('sessions.id'))
    expires_at: Mapped[datetime]
    is_used: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
