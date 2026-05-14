from .base import *

if TYPE_CHECKING:
    from order import Order


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str] = mapped_column(String(128))
    phone_number: Mapped[str] = mapped_column(String(16))
    address: Mapped[str] = mapped_column(String(512))

    orders: Mapped[list[Order]] = relationship("Order",
                                                       back_populates="user",
                                                       cascade="all, delete-orphan",
                                                       passive_deletes=True)

    def __repr__(self):
        return f'User #{self.id} ({self.first_name} {self.last_name}, {self.phone_number}, {self.address})'

