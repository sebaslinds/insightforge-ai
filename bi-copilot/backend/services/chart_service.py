from typing import Any, Literal


ChartType = Literal["bar", "line", "table"]
NUMERIC_FIELDS = ("revenue", "price", "quantity", "total_revenue", "total_sales")
DIMENSION_FIELDS = ("product", "category")


def _has_numeric_value(data: list[dict[str, Any]], field: str) -> bool:
    return any(isinstance(row.get(field), (int, float)) for row in data)


def suggest_chart(data: list[dict[str, Any]]) -> dict[str, str]:
    if not data:
        return {"type": "table", "x": "", "y": ""}

    fields = set(data[0].keys())

    if "date" in fields:
        for metric in NUMERIC_FIELDS:
            if metric in fields and _has_numeric_value(data, metric):
                return {"type": "line", "x": "date", "y": metric}

    for dimension in DIMENSION_FIELDS:
        if dimension not in fields:
            continue
        for metric in NUMERIC_FIELDS:
            if metric in fields and _has_numeric_value(data, metric):
                return {"type": "bar", "x": dimension, "y": metric}

    return {"type": "table", "x": "", "y": ""}
