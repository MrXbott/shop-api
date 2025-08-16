from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class SessionFromDB(BaseModel):
    id: str
    user_id: int
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    is_active: bool

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)