from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.exceptions import HTTPException
from psycopg2.errors import ForeignKeyViolation, IntegrityError
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from alchemy import get_db
from alchemy.entities import Courier
from schema import CourierSchema, ResponseWrapper, CourierCreateSchema

router = APIRouter(
    prefix="/couriers",
    tags=["couriers"],
)


@router.get('/', response_model=ResponseWrapper[CourierSchema])
async def get_couriers(db: Session = Depends(get_db),
                    sort: str = Query('id'),
                    order: Literal['asc', 'desc'] = 'asc',
                    page: int = Query(1, ge=1),
                    size: int = Query(10, ge=1, le=100),
                    filter: str | None = Query(None)
                    ):
    courier_columns = Courier.__table__.columns.keys()
    if sort not in courier_columns:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort parameter. Available: {courier_columns}")

    select_query = select(Courier)

    if filter:
        search_filter = f'%{filter}%'

        select_query = select_query.where(or_(
            Courier.first_name.ilike(search_filter),
            Courier.last_name.ilike(search_filter),
            Courier.phone_number.ilike(search_filter),
        ))

    count_query = select(func.count()).select_from(select_query.subquery())
    total = db.scalar(count_query)

    sort_col = getattr(Courier, sort)
    if order == 'desc':
        sort_col = sort_col.desc()

    offset = (page - 1) * size

    select_query = select_query.order_by(sort_col).offset(offset).limit(size)

    couriers = db.scalars(select_query).all()

    return {
        'items': couriers,
        'total': total,
        'page': page,
        'size': size
    }


@router.get('/{courier_id}', response_model=CourierSchema)
async def get_courier_by_id(courier_id: int,
                         db: Session = Depends(get_db)):
    courier = db.get(Courier, courier_id)
    if not courier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier not found")

    return courier

@router.post('/', response_model=CourierSchema, status_code=status.HTTP_201_CREATED)
async def insert_courier(courier: CourierCreateSchema,
                         db: Session = Depends(get_db)):
    new_courier = Courier(**courier.model_dump())

    try:
        db.add(new_courier)

        db.commit()

        db.refresh(new_courier)

        return new_courier
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Courier already exists")

@router.put('/{courier_id}', response_model=CourierSchema)
async def update_courier(courier_id: int,
                      courier: CourierCreateSchema,
                      db: Session = Depends(get_db)):
    courier_found = db.get(Courier, courier_id)
    if not courier_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier not found")

    new_courier = courier.model_dump()

    for key, value in new_courier.items():
        setattr(courier_found, key, value)

    db.commit()
    db.refresh(courier_found)

    return courier_found

@router.delete('/{courier_id}', status_code=status.HTTP_200_OK)
async def delete_courier(courier_id: int,
                      db: Session = Depends(get_db)):
    courier = db.get(Courier, courier_id)
    if not courier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Courier does not exist")

    try:
        db.delete(courier)
        db.commit()

        return Response('Courier deleted successfully', status.HTTP_200_OK)
    except ForeignKeyViolation as e:
        return Response(e.pgerror, status.HTTP_424_FAILED_DEPENDENCY)
    except Exception as e:
        return Response(e.__repr__(), status.HTTP_400_BAD_REQUEST)
