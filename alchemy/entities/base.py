from sqlalchemy import Integer, String, ForeignKey, Numeric, DateTime, Enum, SmallInteger
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

class Base(DeclarativeBase):
    pass