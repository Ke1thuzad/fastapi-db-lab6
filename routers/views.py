from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from alchemy import get_db
from alchemy.entities import TopFrequentDishes, AverageOrderPositionPrice
from schema import TopFrequentDishesSchema, AverageOrderPositionPriceSchema

router = APIRouter(
    prefix="/views",
    tags=["views"],
)

@router.get("/top10-frequent-dishes/", response_model=List[TopFrequentDishesSchema])
async def get_top10_frequent_dishes(db: Session = Depends(get_db)):
    top10 = db.scalars(select(TopFrequentDishes)).all()

    return top10

@router.get("/avg-order-position-price/", response_model=List[AverageOrderPositionPriceSchema])
async def get_avg_order_position_price(db: Session = Depends(get_db)):
    avg_price = db.scalars(select(AverageOrderPositionPrice).limit(10)).all()

    return avg_price
