SALES_SCHEMA = {
    "table": "sales",
    "columns": [
        {"name": "id", "type": "integer", "description": "Primary key"},
        {"name": "product", "type": "text", "description": "Product name"},
        {"name": "category", "type": "text", "description": "Product category"},
        {"name": "price", "type": "float", "description": "Unit sale price"},
        {"name": "quantity", "type": "integer", "description": "Units sold"},
        {"name": "date", "type": "date", "description": "Sale date"},
        {"name": "customer_id", "type": "text", "description": "Customer identifier"},
    ],
    "metrics": [
        {"name": "revenue", "expression": "price * quantity"},
        {"name": "units_sold", "expression": "SUM(quantity)"},
        {"name": "average_unit_price", "expression": "AVG(price)"},
    ],
}


def get_sales_schema_prompt() -> str:
    columns = "\n".join(
        f"- {column['name']} ({column['type']}): {column['description']}"
        for column in SALES_SCHEMA["columns"]
    )
    metrics = "\n".join(
        f"- {metric['name']}: {metric['expression']}"
        for metric in SALES_SCHEMA["metrics"]
    )
    return f"""
Table: {SALES_SCHEMA["table"]}
Columns:
{columns}

Known metrics:
{metrics}
""".strip()
