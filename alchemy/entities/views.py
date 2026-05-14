from decimal import Decimal

from .base import *

class TopFrequentDishes(Base):
    __tablename__ = 'top10_freq_dishes'

    title: Mapped[str] = mapped_column(primary_key=True)
    total_quantity: Mapped[int]
    rest_title: Mapped[str]
    rating: Mapped[Decimal]


class AverageOrderPositionPrice(Base):
    __tablename__ = 'average_order_position_price'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    avg_order_price: Mapped[Decimal]
    order_amount: Mapped[int]