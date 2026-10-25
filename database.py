"""Small SQLite inventory database with approved read-only queries."""
import sqlite3
from settings import DATABASE_FILE

SAMPLE_PRODUCTS = [
    (101, "Notebook", "Stationery", 12.50, 5, 10),
    (102, "Ballpoint Pen", "Stationery", 2.80, 60, 20),
    (103, "USB Drive", "Electronics", 32.00, 8, 10),
    (104, "Wireless Mouse", "Electronics", 45.00, 16, 8),
    (105, "Folder", "Stationery", 4.50, 12, 15),
    (106, "Keyboard", "Electronics", 79.00, 4, 6),
    (107, "Water Bottle", "Accessories", 18.00, 25, 10),
    (108, "Laptop Stand", "Accessories", 65.00, 7, 5),
]


def initialize_database():
    """Create sample database once; retain existing user changes."""
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_FILE) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Category TEXT NOT NULL,
            UnitPrice REAL NOT NULL,
            Quantity INTEGER NOT NULL,
            ReorderLevel INTEGER NOT NULL
        )""")
        count = db.execute("SELECT COUNT(*) FROM Products").fetchone()[0]
        if count == 0:
            db.executemany(
                "INSERT INTO Products VALUES (?, ?, ?, ?, ?, ?)",
                SAMPLE_PRODUCTS,
            )


def select_rows(query, parameters=()):
    """Execute only developer-defined SELECT statements, not model SQL."""
    with sqlite3.connect(DATABASE_FILE) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only = ON")
        return [dict(row) for row in db.execute(query, parameters).fetchall()]


def list_low_stock():
    """Return products at or below their reorder level."""
    rows = select_rows("""SELECT Name, Quantity, ReorderLevel
        FROM Products WHERE Quantity <= ReorderLevel
        ORDER BY Name""")
    return {"count": len(rows), "products": rows}


def find_product(product_name):
    """Look up matching names using a parameterized query."""
    if (not isinstance(product_name, str)
            or not 1 <= len(product_name.strip()) <= 60):
        raise ValueError("Enter a product name of 1 to 60 characters.")
    # Treat % and _ as literal characters, not SQL LIKE wildcards.
    term = product_name.strip()
    term = term.replace("\\", "\\\\").replace("%", "\\%")
    term = term.replace("_", "\\_")
    rows = select_rows("""SELECT Name, Category, UnitPrice, Quantity
        FROM Products WHERE Name LIKE ? ESCAPE '\\' COLLATE NOCASE
        ORDER BY Name LIMIT 10""", (f"%{term}%",))
    return {"count": len(rows), "products": rows}


def list_category(category):
    """List stock in the specified category."""
    if not isinstance(category, str) or not 1 <= len(category.strip()) <= 40:
        raise ValueError("Enter a category of 1 to 40 characters.")
    rows = select_rows("""SELECT Name, UnitPrice, Quantity
        FROM Products WHERE Category = ? COLLATE NOCASE
        ORDER BY Name LIMIT 30""", (category.strip(),))
    return {"count": len(rows), "products": rows}


def inventory_value():
    """Compute total inventory value in Malaysian ringgit."""
    rows = select_rows("""SELECT COUNT(*) AS ProductCount,
        COALESCE(SUM(Quantity * UnitPrice), 0) AS TotalValue
        FROM Products""")
    return {"products": rows[0]["ProductCount"],
            "total_value_rm": round(rows[0]["TotalValue"], 2)}
