from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, Json, field_validator

from models.weatherapi_response import WeatherApiResponse


# Pydantic V2
class WeatherForecast(BaseModel):
    id: Optional[int] = None
    date: datetime = Field(default_factory=datetime.now)
    # json_obj: Optional[Json[Any]] = None
    json_obj: Optional[Json[WeatherApiResponse]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    # @field_validator("title", mode="before")
    # def title_must_be_valid(cls, value):
    #     if len(value) < 2:
    #         raise ValueError("Title must be at least 2 characters long.")
    #     return value

    # Custom validator for the created_at field to ensure it's always set
    @field_validator("created_at", mode="before")
    def set_created_at(cls, v: datetime) -> datetime:
        return v or datetime.now()

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
