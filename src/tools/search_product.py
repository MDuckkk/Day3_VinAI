from src.tools.init_db import get_connection

def search_product(query: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, price, category FROM products
        WHERE name LIKE ? OR category LIKE ?
    """, (f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"Không tìm thấy sản phẩm nào với từ khóa '{query}'"

    result = "\n".join([f"{r[0]} - {r[1]} - {r[2]:,}đ - {r[3]}" for r in rows])
    return f"Tìm thấy {len(rows)} sản phẩm:\n{result}"

TOOL_SPEC = {
    "name": "search_product",
    "description": "Tìm kiếm sản phẩm trong cửa hàng theo tên hoặc danh mục. Input: chuỗi tìm kiếm, ví dụ 'iPhone' hoặc 'Laptop'.",
    "func": search_product
}
