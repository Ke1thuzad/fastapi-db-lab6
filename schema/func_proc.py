from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class OrderHistorySchema(BaseModel):
    user_id: int
    order_id: int
    model_config = ConfigDict(from_attributes=True)

class UserRegistrationHistorySchema(BaseModel):
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class OrderCorrectnessResponse(BaseModel):
    order_id: int
    is_correct: bool

class TipCourierRequest(BaseModel):
    tip_amount: Decimal = Field(..., ge=0)