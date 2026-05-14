from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, select, func, Select, desc
from sqlalchemy.orm import Session

from alchemy import get_db
from alchemy.entities import OrderContent, Courier, User, Order
from schema import (
    OrderCorrectnessResponse,
    TipCourierRequest
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

@router.get('/top10_courier_tips')
async def get_top10_courier_tips(db: Session = Depends(get_db)):
    sql_query = (
        select(Courier)
        .order_by(Courier.tips.desc())
        .limit(10)
    )

    top10 = db.scalars(sql_query).all()

    return top10

@router.get('/top10_user_orders')
async def get_top10_user_orders(db: Session = Depends(get_db)):
    sel: Select = select(User)

    sql_query = (
        select(User, func.count(Order.id).label('order_count'))
        .join(User.orders)
        .group_by(User.id)
        .order_by(desc('order_count'))
        .limit(10)
    )

    top10 = db.execute(sql_query).all()

    out = []
    for user_obj, count in top10:
        user_data = {
            "id": user_obj.id,
            "first_name": user_obj.first_name,
            "last_name": user_obj.last_name,
            "orders_count": count
        }
        out.append(user_data)

    return out