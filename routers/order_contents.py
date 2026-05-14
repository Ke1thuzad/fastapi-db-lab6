from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.exceptions import HTTPException
from psycopg2.errors import ForeignKeyViolation, IntegrityError
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from alchemy import get_db
from alchemy.entities import OrderContent
from schema import OrderContentSchema, ResponseWrapper

router = APIRouter(
    prefix="/order_contents",
    tags=["order_contents"],
)


@router.get('/', response_model=ResponseWrapper[OrderContentSchema])
async def get_order_contents(db: Session = Depends(get_db),
                    sort: str = Query('order_id'),
                    order: Literal['asc', 'desc'] = 'asc',
                    page: int = Query(1, ge=1),
                    size: int = Query(10, ge=1, le=100),
                    filter: int = Query(None, ge=0)
                    ):
    order_content_columns = OrderContent.__table__.columns.keys()
    if sort not in order_content_columns:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort parameter. Available: {order_content_columns}")

    select_query = select(OrderContent)

    if filter:
        select_query = select_query.where(or_(
            OrderContent.order_id == filter,
            OrderContent.dish_id == filter,
            OrderContent.amount == filter,
        ))

    count_query = select(func.count()).select_from(select_query.subquery())
    total = db.scalar(count_query)

    sort_col = getattr(OrderContent, sort)
    if order == 'desc':
        sort_col = sort_col.desc()

    offset = (page - 1) * size

    select_query = select_query.order_by(sort_col).offset(offset).limit(size)

    order_contents = db.scalars(select_query).all()

    return {
        'items': order_contents,
        'total': total,
        'page': page,
        'size': size
    }


@router.get('/{order_id}/{dish_id}', response_model=OrderContentSchema)
async def get_order_content_by_id(order_id: int,
                                  dish_id: int,
                                  db: Session = Depends(get_db)):
    order_content = db.get(OrderContent, (order_id, dish_id))
    if not order_content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order content not found")

    return order_content

@router.post('/', response_model=OrderContentSchema, status_code=status.HTTP_201_CREATED)
async def insert_order_content(order_content: OrderContentSchema,
                              db: Session = Depends(get_db)):
    new_order_content = OrderContent(**order_content.model_dump())

    try:
        db.add(new_order_content)

        db.commit()

        db.refresh(new_order_content)

        return new_order_content
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order content already exists")

@router.put('/{order_id}/{dish_id}', response_model=OrderContentSchema)
async def update_order_content(order_id: int,
                               dish_id: int,
                               order_content: OrderContentSchema,
                               db: Session = Depends(get_db)):
    order_content_found = db.get(OrderContent, (order_id, dish_id))
    if not order_content_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order content not found")

    new_order_content = order_content.model_dump()

    try:
        for key, value in new_order_content.items():
            setattr(order_content_found, key, value)

        db.commit()
        db.refresh(order_content_found)

        return order_content_found
    except IntegrityError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.pgerror)

@router.delete('/{order_id}/{dish_id}', status_code=status.HTTP_200_OK)
async def delete_order_content(order_id: int,
                               dish_id: int,
                               db: Session = Depends(get_db)):
    order_content = db.get(OrderContent, (order_id, dish_id))
    if not order_content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order content does not exist")

    try:
        db.delete(order_content)
        db.commit()
    except ForeignKeyViolation as e:
        db.rollback()
        return Response(e.pgerror, status.HTTP_424_FAILED_DEPENDENCY)
    except Exception as e:
        db.rollback()
        return Response(e.__repr__(), status.HTTP_400_BAD_REQUEST)