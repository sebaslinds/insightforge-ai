import logging
from datetime import date

from sqlalchemy import func

try:
    from database import SessionLocal, init_db
    from models import Sale
except ModuleNotFoundError:
    from backend.database import SessionLocal, init_db
    from backend.models import Sale


logger = logging.getLogger(__name__)

SALES = [
    Sale(id=1, product="Laptop Pro 14", category="Computers", price=1499.0, quantity=2, date=date(2026, 1, 5), customer_id="C-1001"),
    Sale(id=2, product="Noise Canceling Headphones", category="Audio", price=249.0, quantity=5, date=date(2026, 1, 6), customer_id="C-1002"),
    Sale(id=3, product="USB-C Hub", category="Accessories", price=79.0, quantity=9, date=date(2026, 1, 7), customer_id="C-1003"),
    Sale(id=4, product="Laptop Pro 14", category="Computers", price=1499.0, quantity=1, date=date(2026, 1, 8), customer_id="C-1004"),
    Sale(id=5, product="Mechanical Keyboard", category="Accessories", price=139.0, quantity=6, date=date(2026, 1, 9), customer_id="C-1005"),
    Sale(id=6, product="4K Monitor", category="Displays", price=399.0, quantity=4, date=date(2026, 1, 10), customer_id="C-1006"),
    Sale(id=7, product="Wireless Mouse", category="Accessories", price=59.0, quantity=12, date=date(2026, 1, 11), customer_id="C-1007"),
    Sale(id=8, product="Studio Microphone", category="Audio", price=189.0, quantity=3, date=date(2026, 1, 12), customer_id="C-1008"),
    Sale(id=9, product="4K Monitor", category="Displays", price=399.0, quantity=5, date=date(2026, 1, 13), customer_id="C-1009"),
    Sale(id=10, product="Laptop Pro 14", category="Computers", price=1499.0, quantity=3, date=date(2026, 1, 14), customer_id="C-1010"),
    Sale(id=11, product="Tablet Air", category="Computers", price=699.0, quantity=4, date=date(2026, 1, 15), customer_id="C-1011"),
    Sale(id=12, product="Noise Canceling Headphones", category="Audio", price=249.0, quantity=7, date=date(2026, 1, 16), customer_id="C-1012"),
]


def seed_database(reset: bool = False) -> int:
    init_db()

    with SessionLocal() as session:
        existing_count = session.query(func.count(Sale.id)).scalar() or 0
        if existing_count and not reset:
            logger.info("Sales table already contains %s rows; skipping seed.", existing_count)
            return existing_count

        if reset:
            session.query(Sale).delete()

        session.add_all(
            [
                Sale(
                    id=sale.id,
                    product=sale.product,
                    category=sale.category,
                    price=sale.price,
                    quantity=sale.quantity,
                    date=sale.date,
                    customer_id=sale.customer_id,
                )
                for sale in SALES
            ]
        )
        session.commit()
        logger.info("Seeded %s e-commerce sales rows.", len(SALES))
        return len(SALES)
