import json
from crewai.tools import tool
from app.db import get_conn


@tool("recommend_food")
def recommend_food(max_price: float = None, vegetarian: int = None, spicy: int = None) -> str:
    """
    Recommend food items based on user preferences.
    Args:
        max_price: Maximum price in Tomans
        vegetarian: 1 for vegetarian, 0 for non-vegetarian, None for all
        spicy: 1 for spicy, 0 for non-spicy, None for all
    """
    conn = get_conn()
    cur = conn.cursor()

    query = "SELECT * FROM foods WHERE 1=1"
    params = []

    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)
    if vegetarian is not None:
        query += " AND vegetarian = ?"
        params.append(vegetarian)
    if spicy is not None:
        query += " AND spicy = ?"
        params.append(spicy)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "هیچ غذایی با این مشخصات پیدا نشد."

    result = []
    for r in rows:
        result.append({
            "id": r[0], "name": r[1], "category": r[2],
            "price": int(r[3]), "calories": r[4],
            "spicy": bool(r[5]), "vegetarian": bool(r[6])
        })
    return json.dumps(result, ensure_ascii=False)
