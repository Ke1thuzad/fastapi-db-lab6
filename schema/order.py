from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from alchemy.entities.order import OrderStatesEnum


class OrderBase(BaseModel):
    order_date: datetime = Field(default_factory=datetime.now)
    order_state: OrderStatesEnum = Field(OrderStatesEnum.processing)
    user_id: int = Field(..., ge=1)
    courier_id: Optional[int] = Field(None, ge=1)


class OrderSchema(OrderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreateSchema(OrderBase):
    pass