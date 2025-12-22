from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.program import ProgramSimple
from app.schemas.user import UserBase


class ActivityBase(BaseModel):
    description: str
    evidence_url: str | None = None
    performed_at: datetime | None = None


class ActivityCreate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    id: int
    created_at: datetime
    user: Optional[UserBase] = None
    program: Optional[ProgramSimple] = None

    model_config = ConfigDict(from_attributes=True)
