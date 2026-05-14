from .base import *

if TYPE_CHECKING:
    from order import Order


class OrderContent(Base):
    __tablename__ = 'order_contents'

    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    dish_id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(SmallInteger)

    order: Mapped[Order] = relationship(back_populates='order_content')

    def __repr__(self):
        return f'Order #{self.order_id}. Dish #{self.dish_id}. Amount: {self.amount}'