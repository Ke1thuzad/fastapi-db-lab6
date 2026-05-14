from pydantic import BaseModel, ConfigDict, Field


class OrderContentSchema(BaseModel):
    order_id: int = Field(1, ge=1)
    dish_id: int = Field(1, ge=1)
    amount: int = Field(1, ge=1)

    model_config = ConfigDict(from_attributes=True)