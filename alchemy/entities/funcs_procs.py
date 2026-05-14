from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class OrderHistory(Base):
    __tablename__ = 'order_history'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(primary_key=True)


class UserRegistrationHistory(Base):
    __tablename__ = 'user_registration_history'

    user_id: Mapped[int] = mapped_column(primary_key=True)