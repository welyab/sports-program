from sqlalchemy import String, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.database import Base
from pydantic import BaseModel, ConfigDict

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    program_id: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    evidence_url: Mapped[str] = mapped_column(String, nullable=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ActivityBase(BaseModel):
    description: str
    evidence_url: str
    performed_at: datetime

class ActivityCreate(ActivityBase):
    pass

class ActivityRead(ActivityBase):
    id: int
    user_id: int
    program_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
