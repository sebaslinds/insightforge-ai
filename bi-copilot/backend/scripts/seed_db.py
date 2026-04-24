from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from services.seed_service import seed_database


def seed() -> None:
    seed_database(reset=True)


if __name__ == "__main__":
    seed()
    print("Seeded e-commerce sales rows.")
