import enum
from datetime import datetime

from alchemy.entities.order_content import OrderContent
from .base import *

if TYPE_CHECKING:
    from user import User
    from courier import Courier


class OrderStatesEnum(enum.IntEnum):
    processing = 1
    accepted = 2
    cooking = 3
    in_delivery = 4
    delivered = 5

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}>"


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    order_state: Mapped[OrderStatesEnum] = mapped_column(Enum(OrderStatesEnum, native_enum=True), default=OrderStatesEnum.processing)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    courier_id: Mapped[int] = mapped_column(ForeignKey('couriers.id', ondelete='SET NULL'), nullable=True, default=None)

    user: Mapped[User] = relationship(back_populates='orders')
    courier: Mapped[Courier] = relationship(back_populates='orders')
    order_content: Mapped[OrderContent] = relationship(back_populates='order',
                                                       cascade="all, delete-orphan",
                                                       passive_deletes=True)

    def __repr__(self):
        return (f'Order #{self.id} (Order date: {self.order_date}. Order state: {self.order_state}. '
                f'User id: {self.user_id}. Courier id: {self.courier_id})')


