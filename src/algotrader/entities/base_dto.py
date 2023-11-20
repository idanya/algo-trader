from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    _types: ClassVar[dict[str, type]] = {}

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
