from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

try:
    from database import Base
except ModuleNotFoundError:
    from backend.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[object] = mapped_column(Date, nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
