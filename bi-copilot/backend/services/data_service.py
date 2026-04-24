from functools import lru_cache
from pathlib import Path

import pandas as pd

try:
    from errors import DataLoadError
except ModuleNotFoundError:
    from backend.errors import DataLoadError


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SALES_DATASET_PATH = DATA_DIR / "sales.csv"
REQUIRED_SALES_COLUMNS = {
    "id",
    "product",
    "category",
    "price",
    "quantity",
    "date",
    "customer_id",
}


@lru_cache
def load_sales_data() -> pd.DataFrame:
    if not SALES_DATASET_PATH.exists():
        raise DataLoadError("Sales dataset file is missing.")

    try:
        dataframe = pd.read_csv(
            SALES_DATASET_PATH,
            parse_dates=["date"],
        )
    except Exception as exc:
        raise DataLoadError("Sales dataset could not be read.") from exc

    missing_columns = REQUIRED_SALES_COLUMNS - set(dataframe.columns)
    if missing_columns:
        raise DataLoadError("Sales dataset schema is invalid.")

    return dataframe
