from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.exceptions import HTTPException
from psycopg2.errors import ForeignKeyViolation, IntegrityError
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from alchemy import get_db
from alchemy.entities import User
from schema import UserSchema, ResponseWrapper, UserCreateSchema

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get('/', response_model=ResponseWrapper[UserSchema])
async def get_users(db: Session = Depends(get_db),
                    sort: str = Query('id'),
                    order: Literal['asc', 'desc'] = 'asc',
                    page: int = Query(1, ge=1),
                    size: int = Query(10, ge=1, le=100),
                    filter: str | None = Query(None)
                    ):
    user_columns = User.__table__.columns.keys()
    if sort not in user_columns:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid sort parameter. Available: {user_columns}")

    select_query = select(User)

    if filter:
        search_filter = f'%{filter}%'

        select_query = select_query.where(or_(
            User.first_name.ilike(search_filter),
            User.last_name.ilike(search_filter),
            User.phone_number.ilike(search_filter),
            User.address.ilike(search_filter)
        ))

    count_query = select(func.count()).select_from(select_query.subquery())
    total = db.scalar(count_query)

    sort_col = getattr(User, sort)
    if order == 'desc':
        sort_col = sort_col.desc()

    offset = (page - 1) * size

    select_query = select_query.order_by(sort_col).offset(offset).limit(size)

    users = db.scalars(select_query).all()

    return {
        'items': users,
        'total': total,
        'page': page,
        'size': size
    }


@router.get('/{user_id}', response_model=UserSchema)
async def get_user_by_id(user_id: int,
                         db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

@router.post('/', response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def insert_user(user: UserCreateSchema,
                      db: Session = Depends(get_db)):
    new_user = User(**user.model_dump())

    try:
        db.add(new_user)

        db.commit()

        db.refresh(new_user)

        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

@router.put('/{user_id}', response_model=UserSchema)
async def update_user(user_id: int,
                      user: UserCreateSchema,
                      db: Session = Depends(get_db)):
    user_found = db.get(User, user_id)
    if not user_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_user = user.model_dump()

    for key, value in new_user.items():
        setattr(user_found, key, value)

    db.commit()
    db.refresh(user_found)

    return user_found

@router.delete('/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user(user_id: int,
                      db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    try:
        db.delete(user)
        db.commit()

        return Response('User deleted successfully', status.HTTP_200_OK)
    except ForeignKeyViolation as e:
        return Response(e.pgerror, status.HTTP_424_FAILED_DEPENDENCY)
    except Exception as e:
        return Response(e.__repr__(), status.HTTP_400_BAD_REQUEST)
