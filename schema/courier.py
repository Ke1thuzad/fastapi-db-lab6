from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class CourierBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=128)
    last_name: str = Field(..., min_length=1, max_length=128)
    phone_number: str = Field(..., min_length=1, max_length=16)
    orders_completed: int = Field(0, ge=0)
    tips: Decimal = Field(0, ge=0)


class CourierSchema(CourierBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CourierCreateSchema(CourierBase):
    pass