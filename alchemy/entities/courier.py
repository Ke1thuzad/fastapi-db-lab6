from .base import *

if TYPE_CHECKING:
    from order import Order


class Courier(Base):
    __tablename__ = 'couriers'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str] = mapped_column(String(128))
    phone_number: Mapped[str] = mapped_column(String(16))
    orders_completed: Mapped[int]
    tips: Mapped[Numeric] = mapped_column(Numeric(10, 3))

    orders: Mapped[list[Order]] = relationship("Order",
                                                back_populates="courier",
                                                cascade="all, delete-orphan",
                                                passive_deletes=True)

    def __repr__(self):
        return (f'Courier #{self.id} ({self.first_name} {self.last_name}, {self.phone_number}. '
                f'Completed orders: {self.orders_completed}. Tips: {self.tips})')
