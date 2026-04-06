import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "products.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id       TEXT PRIMARY KEY,
            name     TEXT NOT NULL,
            category TEXT NOT NULL,
            price    INTEGER NOT NULL,
            stock    INTEGER NOT NULL,
            specs    TEXT
        )
    """)

    products = [
        ("p001", "iPhone 15 128GB",     "Điện thoại", 22000000, 5, "6.1 inch, chip A16 Bionic, camera 48MP, pin 3279mAh"),
        ("p002", "iPhone 15 256GB",     "Điện thoại", 25000000, 0, "6.1 inch, chip A16 Bionic, camera 48MP, pin 3279mAh"),
        ("p003", "Samsung Galaxy S24",  "Điện thoại", 20000000, 8, "6.2 inch, Snapdragon 8 Gen 3, RAM 12GB, pin 4000mAh"),
        ("p004", "Dell XPS 13",         "Laptop",     28000000, 3, "13.4 inch OLED, Intel Core i5, RAM 16GB, SSD 512GB"),
        ("p005", "MacBook Air M2",      "Laptop",     32000000, 1, "13.6 inch Liquid Retina, chip M2, RAM 8GB, SSD 256GB"),
        ("p006", "iPad Air M2",         "Máy tính bảng", 18000000, 0, "11 inch, chip M2, RAM 8GB, 256GB"),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO products (id, name, category, price, stock, specs)
        VALUES (?, ?, ?, ?, ?, ?)
    """, products)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
