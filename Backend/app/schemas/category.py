"""Category schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_default: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
