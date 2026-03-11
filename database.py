from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db.sqlite3"


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role_id INTEGER NOT NULL REFERENCES role(id)
);

CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS manufacturer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS supplier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS unit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    unit_id INTEGER NOT NULL REFERENCES unit(id),
    price REAL NOT NULL CHECK(price >= 0),
    supplier_id INTEGER NOT NULL REFERENCES supplier(id),
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturer(id),
    category_id INTEGER NOT NULL REFERENCES category(id),
    discount_percent INTEGER NOT NULL DEFAULT 0 CHECK(discount_percent >= 0 AND discount_percent <= 100),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK(stock_quantity >= 0),
    description TEXT NOT NULL,
    image_path TEXT
);

CREATE TABLE IF NOT EXISTS pickup_point (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS order_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS customer_order (
    id INTEGER PRIMARY KEY,
    order_date TEXT NOT NULL,
    delivery_date TEXT NOT NULL,
    pickup_point_id INTEGER NOT NULL REFERENCES pickup_point(id),
    customer_id INTEGER NOT NULL REFERENCES user(id),
    receive_code INTEGER NOT NULL,
    status_id INTEGER NOT NULL REFERENCES order_status(id)
);

CREATE TABLE IF NOT EXISTS order_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES customer_order(id) ON DELETE CASCADE,
    product_article TEXT NOT NULL REFERENCES product(article),
    quantity INTEGER NOT NULL CHECK(quantity > 0)
);
"""


def init_schema() -> None:
    with connect() as connection:
        connection.executescript(SCHEMA_SQL)
        connection.commit()
