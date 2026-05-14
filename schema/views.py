from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class TopFrequentDishesSchema(BaseModel):
    title: str
    total_quantity: int
    rest_title: str
    rating: Decimal = Field(1, ge=1, le=5)

    model_config = ConfigDict(from_attributes=True)


class AverageOrderPositionPriceSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    avg_order_price: Decimal = Field(0, ge=0)
    order_amount: int

    model_config = ConfigDict(from_attributes=True)