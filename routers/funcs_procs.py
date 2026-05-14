from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, select
from sqlalchemy.orm import Session

from alchemy import get_db
from schema import (
    OrderCorrectnessResponse,
    TipCourierRequest
)

router = APIRouter(
    prefix="/operations",
    tags=["operations"],
)

@router.get("/orders/{order_id}/check", response_model=OrderCorrectnessResponse)
async def check_order_correctness(order_id: int, db: Session = Depends(get_db)):
    query = text("SELECT public.check_order_correctness(:order_id)")
    result = db.execute(query, {"order_id": order_id}).scalar()
    return {"order_id": order_id, "is_correct": result}

@router.post("/orders/{order_id}/complete")
async def complete_order(order_id: int, db: Session = Depends(get_db)):
    try:
        db.execute(text("CALL public.complete_order(:order_id)"), {"order_id": order_id})
        db.commit()
        return {"status": "success", "message": f"Order {order_id} completed"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/orders/{order_id}/tip")
async def tip_courier(order_id: int, tip_data: TipCourierRequest, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("CALL public.tip_courier(:order_id, :tip_amount)"),
            {"order_id": order_id, "tip_amount": tip_data.tip_amount}
        )
        db.commit()
        return {"status": "success", "message": "Tip added"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))