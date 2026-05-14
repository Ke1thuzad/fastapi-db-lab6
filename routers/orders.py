from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.exceptions import HTTPException
from psycopg2.errors import ForeignKeyViolation, IntegrityError
from sqlalchemy import select, func, or_, cast, String, ColumnElement
from sqlalchemy.orm import Session

from alchemy import get_db
from alchemy.entities import Order
from schema import OrderSchema, ResponseWrapper, OrderCreateSchema


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get('/', response_model=ResponseWrapper[OrderSchema])
async def get_orders(db: Session = Depends(get_db),
                    sort: str = Query('id'),
                    order: Literal['asc', 'desc'] = 'asc',
                    page: int = Query(1, ge=1),
                    size: int = Query(10, ge=1, le=100),
                    filter: str | None = Query(None)
                    ):
    order_columns = Order.__table__.columns.keys()
    if sort not in order_columns:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort parameter. Available: {order_columns}")

    select_query = select(Order)

    if filter:
        conditions: list[ColumnElement[bool]] = [cast(Order.order_date, String).ilike(f'%{filter}%')]

        if filter.isdigit():
            conditions.append(Order.user_id == int(filter))
            conditions.append(Order.courier_id == int(filter))

        select_query = select_query.where(or_(*conditions))

    count_query = select(func.count()).select_from(select_query.subquery())
    total = db.scalar(count_query)

    sort_col = getattr(Order, sort)
    if order == 'desc':
        sort_col = sort_col.desc()

    offset = (page - 1) * size

    select_query = select_query.order_by(sort_col).offset(offset).limit(size)

    orders = db.scalars(select_query).all()

    return {
        'items': orders,
        'total': total,
        'page': page,
        'size': size
    }


@router.get('/{order_id}', response_model=OrderSchema)
async def get_order_by_id(order_id: int,
                         db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order

@router.post('/', response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def insert_order(order: OrderCreateSchema,
                         db: Session = Depends(get_db)):
    new_order = Order(**order.model_dump())

    try:
        db.add(new_order)

        db.commit()

        db.refresh(new_order)

        return new_order
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exists")

@router.put('/{order_id}', response_model=OrderSchema)
async def update_order(order_id: int,
                      order: OrderCreateSchema,
                      db: Session = Depends(get_db)):
    order_found = db.get(Order, order_id)
    if not order_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    new_order = order.model_dump()

    for key, value in new_order.items():
        setattr(order_found, key, value)

    db.commit()
    db.refresh(order_found)

    return order_found

@router.delete('/{order_id}', status_code=status.HTTP_200_OK)
async def delete_order(order_id: int,
                      db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist")

    try:
        db.delete(order)
        db.commit()

        return Response('Order deleted successfully', status.HTTP_200_OK)
    except ForeignKeyViolation as e:
        db.rollback()
        return Response(e.pgerror, status.HTTP_424_FAILED_DEPENDENCY)
    except Exception as e:
        db.rollback()
        return Response(e.__repr__(), status.HTTP_400_BAD_REQUEST)