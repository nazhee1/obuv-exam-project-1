from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any

from .config import (
    DB_PATH,
    DUMP_PATH,
    ORDER_STATUSES,
    ORDERS_XLSX,
    PICKUP_POINTS_XLSX,
    PRODUCTS_XLSX,
    ROLE_ADMIN,
    ROLE_CLIENT,
    ROLE_MANAGER,
    USERS_XLSX,
)
from .xlsx_reader import clean_text, normalize_excel_date, read_xlsx_rows


class DatabaseManager:
    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            self._create_schema(connection)
            if self._is_empty(connection):
                self._seed_database(connection)
            connection.commit()

    def reset(self) -> None:
        if self.db_path.exists():
            self.db_path.unlink()
        self.initialize()

    def create_dump_file(self, dump_path: str | Path = DUMP_PATH) -> Path:
        self.initialize()
        dump_target = Path(dump_path)
        with self.connect() as connection:
            dump_sql = "\n".join(connection.iterdump()) + "\n"
        dump_target.write_text(dump_sql, encoding="utf-8")
        return dump_target

    def authenticate(self, login: str, password: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT id, full_name, login, role
                FROM users
                WHERE login = ? AND password = ?
                """,
                (clean_text(login), clean_text(password)),
            ).fetchone()
        return dict(row) if row else None

    def get_demo_accounts(self) -> list[dict[str, Any]]:
        roles = [ROLE_ADMIN, ROLE_MANAGER, ROLE_CLIENT]
        result: list[dict[str, Any]] = []
        with self.connect() as connection:
            for role in roles:
                row = connection.execute(
                    """
                    SELECT role, full_name, login, password
                    FROM users
                    WHERE role = ?
                    ORDER BY id
                    LIMIT 1
                    """,
                    (role,),
                ).fetchone()
                if row:
                    result.append(dict(row))
        return result

    def get_summary(self) -> dict[str, int]:
        with self.connect() as connection:
            products = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            users = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            orders = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        return {"products": products, "users": users, "orders": orders}

    def list_products(
        self,
        search: str = "",
        category: str = "",
        sort_key: str = "name_asc",
    ) -> list[dict[str, Any]]:
        sort_map = {
            "name_asc": "name COLLATE NOCASE ASC",
            "name_desc": "name COLLATE NOCASE DESC",
            "price_asc": "price ASC",
            "price_desc": "price DESC",
            "discount_desc": "discount_percent DESC, name COLLATE NOCASE ASC",
            "stock_desc": "stock_quantity DESC, name COLLATE NOCASE ASC",
        }
        order_clause = sort_map.get(sort_key, sort_map["name_asc"])
        where_clauses = ["1 = 1"]
        params: list[Any] = []

        if clean_text(search):
            pattern = f"%{clean_text(search)}%"
            where_clauses.append(
                """
                (
                    article LIKE ?
                    OR name LIKE ?
                    OR manufacturer LIKE ?
                    OR supplier LIKE ?
                    OR description LIKE ?
                )
                """
            )
            params.extend([pattern] * 5)

        if clean_text(category):
            where_clauses.append("category = ?")
            params.append(clean_text(category))

        query = f"""
            SELECT
                article,
                name,
                unit,
                price,
                supplier,
                manufacturer,
                category,
                discount_percent,
                stock_quantity,
                description,
                photo,
                ROUND(price * (100 - discount_percent) / 100.0, 2) AS discount_price
            FROM products
            WHERE {" AND ".join(where_clauses)}
            ORDER BY {order_clause}
        """

        with self.connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_product(self, article: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    article,
                    name,
                    unit,
                    price,
                    supplier,
                    manufacturer,
                    category,
                    discount_percent,
                    stock_quantity,
                    description,
                    photo
                FROM products
                WHERE article = ?
                """,
                (article,),
            ).fetchone()
        return dict(row) if row else None

    def get_product_reference_data(self) -> dict[str, list[str]]:
        with self.connect() as connection:
            categories = self._distinct_values(connection, "category")
            suppliers = self._distinct_values(connection, "supplier")
            manufacturers = self._distinct_values(connection, "manufacturer")
            units = self._distinct_values(connection, "unit")
            photos = [
                row["photo"]
                for row in connection.execute(
                    """
                    SELECT DISTINCT photo
                    FROM products
                    WHERE photo <> ''
                    ORDER BY photo
                    """
                ).fetchall()
            ]
        return {
            "categories": categories,
            "suppliers": suppliers,
            "manufacturers": manufacturers,
            "units": units,
            "photos": photos,
        }

    def save_product(
        self,
        payload: dict[str, Any],
        original_article: str | None = None,
    ) -> None:
        data = self._validate_product_payload(payload)
        with self.connect() as connection:
            try:
                if original_article:
                    connection.execute(
                        """
                        UPDATE products
                        SET
                            article = ?,
                            name = ?,
                            unit = ?,
                            price = ?,
                            supplier = ?,
                            manufacturer = ?,
                            category = ?,
                            discount_percent = ?,
                            stock_quantity = ?,
                            description = ?,
                            photo = ?
                        WHERE article = ?
                        """,
                        (
                            data["article"],
                            data["name"],
                            data["unit"],
                            data["price"],
                            data["supplier"],
                            data["manufacturer"],
                            data["category"],
                            data["discount_percent"],
                            data["stock_quantity"],
                            data["description"],
                            data["photo"],
                            original_article,
                        ),
                    )
                else:
                    connection.execute(
                        """
                        INSERT INTO products (
                            article,
                            name,
                            unit,
                            price,
                            supplier,
                            manufacturer,
                            category,
                            discount_percent,
                            stock_quantity,
                            description,
                            photo
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            data["article"],
                            data["name"],
                            data["unit"],
                            data["price"],
                            data["supplier"],
                            data["manufacturer"],
                            data["category"],
                            data["discount_percent"],
                            data["stock_quantity"],
                            data["description"],
                            data["photo"],
                        ),
                    )
                connection.commit()
            except sqlite3.IntegrityError as exc:
                raise ValueError(
                    "Товар с таким артикулом уже существует или нарушает связи с заказами."
                ) from exc

    def delete_product(self, article: str) -> None:
        with self.connect() as connection:
            try:
                connection.execute("DELETE FROM products WHERE article = ?", (article,))
                connection.commit()
            except sqlite3.IntegrityError as exc:
                raise ValueError(
                    "Нельзя удалить товар, который уже используется в заказах."
                ) from exc

    def list_orders(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    o.order_number,
                    o.items_text,
                    o.order_date,
                    o.delivery_date,
                    o.pickup_point_id,
                    p.address AS pickup_point_address,
                    o.customer_name,
                    o.customer_user_id,
                    o.pickup_code,
                    o.status
                FROM orders AS o
                LEFT JOIN pickup_points AS p
                    ON p.id = o.pickup_point_id
                ORDER BY o.order_number
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_order(self, order_number: int) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    o.order_number,
                    o.items_text,
                    o.order_date,
                    o.delivery_date,
                    o.pickup_point_id,
                    p.address AS pickup_point_address,
                    o.customer_name,
                    o.customer_user_id,
                    o.pickup_code,
                    o.status
                FROM orders AS o
                LEFT JOIN pickup_points AS p
                    ON p.id = o.pickup_point_id
                WHERE o.order_number = ?
                """,
                (order_number,),
            ).fetchone()
        return dict(row) if row else None

    def get_pickup_points(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT id, address FROM pickup_points ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_users(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, full_name, login, role
                FROM users
                ORDER BY full_name COLLATE NOCASE ASC, role ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def save_order(
        self,
        payload: dict[str, Any],
        original_number: int | None = None,
    ) -> None:
        data = self._validate_order_payload(payload)
        with self.connect() as connection:
            for article, _quantity in data["parsed_items"]:
                exists = connection.execute(
                    "SELECT 1 FROM products WHERE article = ?",
                    (article,),
                ).fetchone()
                if not exists:
                    raise ValueError(f"Товар с артикулом {article} не найден.")

            try:
                if original_number is None:
                    cursor = connection.execute(
                        """
                        INSERT INTO orders (
                            order_number,
                            items_text,
                            order_date,
                            delivery_date,
                            pickup_point_id,
                            customer_name,
                            customer_user_id,
                            pickup_code,
                            status
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            data["order_number"],
                            data["items_text"],
                            data["order_date"],
                            data["delivery_date"],
                            data["pickup_point_id"],
                            data["customer_name"],
                            data["customer_user_id"],
                            data["pickup_code"],
                            data["status"],
                        ),
                    )
                    order_id = cursor.lastrowid
                else:
                    connection.execute(
                        """
                        UPDATE orders
                        SET
                            order_number = ?,
                            items_text = ?,
                            order_date = ?,
                            delivery_date = ?,
                            pickup_point_id = ?,
                            customer_name = ?,
                            customer_user_id = ?,
                            pickup_code = ?,
                            status = ?
                        WHERE order_number = ?
                        """,
                        (
                            data["order_number"],
                            data["items_text"],
                            data["order_date"],
                            data["delivery_date"],
                            data["pickup_point_id"],
                            data["customer_name"],
                            data["customer_user_id"],
                            data["pickup_code"],
                            data["status"],
                            original_number,
                        ),
                    )
                    order_id = connection.execute(
                        "SELECT id FROM orders WHERE order_number = ?",
                        (data["order_number"],),
                    ).fetchone()["id"]

                self._replace_order_items(connection, order_id, data["parsed_items"])
                connection.commit()
            except sqlite3.IntegrityError as exc:
                raise ValueError(
                    "Заказ с таким номером уже существует или использует неверные связи."
                ) from exc

    def delete_order(self, order_number: int) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM orders WHERE order_number = ?", (order_number,))
            connection.commit()

    def parse_order_items(self, items_text: str) -> list[tuple[str, int]]:
        tokens = [clean_text(part) for part in items_text.split(",") if clean_text(part)]
        if len(tokens) % 2 != 0:
            raise ValueError(
                "Состав заказа нужно указывать парами: артикул, количество."
            )

        parsed_items: list[tuple[str, int]] = []
        for index in range(0, len(tokens), 2):
            article = tokens[index]
            quantity_text = tokens[index + 1]
            try:
                quantity = int(quantity_text)
            except ValueError as exc:
                raise ValueError(
                    f"Количество для товара {article} должно быть целым числом."
                ) from exc
            if quantity <= 0:
                raise ValueError("Количество товара в заказе должно быть больше нуля.")
            parsed_items.append((article, quantity))
        return parsed_items

    def _create_schema(self, connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                login TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pickup_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS products (
                article TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                unit TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                supplier TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                category TEXT NOT NULL,
                discount_percent INTEGER NOT NULL CHECK (discount_percent BETWEEN 0 AND 100),
                stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
                description TEXT NOT NULL,
                photo TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number INTEGER NOT NULL UNIQUE,
                items_text TEXT NOT NULL,
                order_date TEXT NOT NULL,
                delivery_date TEXT NOT NULL,
                pickup_point_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                customer_user_id INTEGER,
                pickup_code TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,
                FOREIGN KEY (customer_user_id) REFERENCES users(id)
                    ON UPDATE CASCADE
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_article TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                FOREIGN KEY (order_id) REFERENCES orders(id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE,
                FOREIGN KEY (product_article) REFERENCES products(article)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            );

            CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
            CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
            """
        )

    def _is_empty(self, connection: sqlite3.Connection) -> bool:
        return connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0

    def _seed_database(self, connection: sqlite3.Connection) -> None:
        for user in self._load_user_rows():
            connection.execute(
                """
                INSERT INTO users (full_name, login, password, role)
                VALUES (?, ?, ?, ?)
                """,
                (user["full_name"], user["login"], user["password"], user["role"]),
            )

        for address in self._load_pickup_point_rows():
            connection.execute(
                "INSERT INTO pickup_points (address) VALUES (?)",
                (address,),
            )

        for product in self._load_product_rows():
            connection.execute(
                """
                INSERT INTO products (
                    article,
                    name,
                    unit,
                    price,
                    supplier,
                    manufacturer,
                    category,
                    discount_percent,
                    stock_quantity,
                    description,
                    photo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["article"],
                    product["name"],
                    product["unit"],
                    product["price"],
                    product["supplier"],
                    product["manufacturer"],
                    product["category"],
                    product["discount_percent"],
                    product["stock_quantity"],
                    product["description"],
                    product["photo"],
                ),
            )

        for order in self._load_order_rows():
            customer_user_id = self._find_user_id_by_name(connection, order["customer_name"])
            cursor = connection.execute(
                """
                INSERT INTO orders (
                    order_number,
                    items_text,
                    order_date,
                    delivery_date,
                    pickup_point_id,
                    customer_name,
                    customer_user_id,
                    pickup_code,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order["order_number"],
                    order["items_text"],
                    order["order_date"],
                    order["delivery_date"],
                    order["pickup_point_id"],
                    order["customer_name"],
                    customer_user_id,
                    order["pickup_code"],
                    order["status"],
                ),
            )
            self._replace_order_items(connection, cursor.lastrowid, order["parsed_items"])

    def _load_product_rows(self) -> list[dict[str, Any]]:
        rows = read_xlsx_rows(PRODUCTS_XLSX)
        products: list[dict[str, Any]] = []
        for row in rows[1:]:
            if not row or not clean_text(row[0]):
                continue
            products.append(
                {
                    "article": clean_text(row[0]),
                    "name": clean_text(row[1]),
                    "unit": clean_text(row[2]),
                    "price": float(clean_text(row[3]).replace(",", ".")),
                    "supplier": clean_text(row[4]),
                    "manufacturer": clean_text(row[5]),
                    "category": clean_text(row[6]),
                    "discount_percent": int(clean_text(row[7]) or "0"),
                    "stock_quantity": int(clean_text(row[8]) or "0"),
                    "description": clean_text(row[9]),
                    "photo": clean_text(row[10]),
                }
            )
        return products

    def _load_user_rows(self) -> list[dict[str, str]]:
        rows = read_xlsx_rows(USERS_XLSX)
        users: list[dict[str, str]] = []
        for row in rows[1:]:
            if not row or not clean_text(row[0]):
                continue
            users.append(
                {
                    "role": clean_text(row[0]),
                    "full_name": clean_text(row[1]),
                    "login": clean_text(row[2]),
                    "password": clean_text(row[3]),
                }
            )
        return users

    def _load_pickup_point_rows(self) -> list[str]:
        rows = read_xlsx_rows(PICKUP_POINTS_XLSX)
        return [clean_text(row[0]) for row in rows if row and clean_text(row[0])]

    def _load_order_rows(self) -> list[dict[str, Any]]:
        rows = read_xlsx_rows(ORDERS_XLSX)
        orders: list[dict[str, Any]] = []
        for row in rows[1:]:
            if not row or not clean_text(row[0]):
                continue
            normalized = list(row[:8]) + [""] * max(0, 8 - len(row))
            items_text = clean_text(normalized[1])
            orders.append(
                {
                    "order_number": int(clean_text(normalized[0])),
                    "items_text": items_text,
                    "order_date": normalize_excel_date(normalized[2]),
                    "delivery_date": normalize_excel_date(normalized[3]),
                    "pickup_point_id": int(clean_text(normalized[4])),
                    "customer_name": clean_text(normalized[5]),
                    "pickup_code": clean_text(normalized[6]),
                    "status": clean_text(normalized[7]),
                    "parsed_items": self.parse_order_items(items_text),
                }
            )
        return orders

    def _validate_product_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        article = clean_text(payload.get("article"))
        name = clean_text(payload.get("name"))
        unit = clean_text(payload.get("unit"))
        supplier = clean_text(payload.get("supplier"))
        manufacturer = clean_text(payload.get("manufacturer"))
        category = clean_text(payload.get("category"))
        description = clean_text(payload.get("description"))
        photo = clean_text(payload.get("photo"))

        if not article:
            raise ValueError("Укажите артикул товара.")
        if not name:
            raise ValueError("Укажите наименование товара.")
        if not unit:
            raise ValueError("Укажите единицу измерения.")
        if not supplier:
            raise ValueError("Укажите поставщика.")
        if not manufacturer:
            raise ValueError("Укажите производителя.")
        if not category:
            raise ValueError("Укажите категорию товара.")
        if not description:
            raise ValueError("Укажите описание товара.")

        try:
            price = float(str(payload.get("price", "")).replace(",", "."))
        except ValueError as exc:
            raise ValueError("Цена должна быть числом.") from exc
        if price < 0:
            raise ValueError("Цена не может быть отрицательной.")

        try:
            discount_percent = int(str(payload.get("discount_percent", "")).replace(",", "."))
        except ValueError as exc:
            raise ValueError("Скидка должна быть целым числом.") from exc
        if not 0 <= discount_percent <= 100:
            raise ValueError("Скидка должна быть в диапазоне от 0 до 100.")

        try:
            stock_quantity = int(str(payload.get("stock_quantity", "")).replace(",", "."))
        except ValueError as exc:
            raise ValueError("Остаток на складе должен быть целым числом.") from exc
        if stock_quantity < 0:
            raise ValueError("Остаток на складе не может быть отрицательным.")

        return {
            "article": article,
            "name": name,
            "unit": unit,
            "price": price,
            "supplier": supplier,
            "manufacturer": manufacturer,
            "category": category,
            "discount_percent": discount_percent,
            "stock_quantity": stock_quantity,
            "description": description,
            "photo": photo,
        }

    def _validate_order_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            order_number = int(clean_text(payload.get("order_number")))
        except ValueError as exc:
            raise ValueError("Номер заказа должен быть целым числом.") from exc

        items_text = clean_text(payload.get("items_text"))
        if not items_text:
            raise ValueError("Укажите состав заказа.")

        try:
            pickup_point_id = int(clean_text(payload.get("pickup_point_id")))
        except ValueError as exc:
            raise ValueError("Выберите корректный пункт выдачи.") from exc

        pickup_code = clean_text(payload.get("pickup_code"))
        if not pickup_code:
            raise ValueError("Укажите код для получения.")

        status = clean_text(payload.get("status")) or ORDER_STATUSES[0]
        if status not in ORDER_STATUSES:
            raise ValueError("Выберите корректный статус заказа.")

        customer_name = clean_text(payload.get("customer_name"))
        customer_user_id_text = clean_text(payload.get("customer_user_id"))
        customer_user_id = int(customer_user_id_text) if customer_user_id_text else None

        if customer_user_id is not None and not customer_name:
            with self.connect() as connection:
                row = connection.execute(
                    "SELECT full_name FROM users WHERE id = ?",
                    (customer_user_id,),
                ).fetchone()
                customer_name = row["full_name"] if row else ""

        if not customer_name:
            raise ValueError("Укажите клиента или заполните ФИО вручную.")

        parsed_items = self.parse_order_items(items_text)

        return {
            "order_number": order_number,
            "items_text": items_text,
            "order_date": clean_text(payload.get("order_date")),
            "delivery_date": clean_text(payload.get("delivery_date")),
            "pickup_point_id": pickup_point_id,
            "customer_name": customer_name,
            "customer_user_id": customer_user_id,
            "pickup_code": pickup_code,
            "status": status,
            "parsed_items": parsed_items,
        }

    def _replace_order_items(
        self,
        connection: sqlite3.Connection,
        order_id: int,
        items: list[tuple[str, int]],
    ) -> None:
        connection.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        for article, quantity in items:
            connection.execute(
                """
                INSERT INTO order_items (order_id, product_article, quantity)
                VALUES (?, ?, ?)
                """,
                (order_id, article, quantity),
            )

    def _find_user_id_by_name(
        self,
        connection: sqlite3.Connection,
        full_name: str,
    ) -> int | None:
        row = connection.execute(
            """
            SELECT id
            FROM users
            WHERE full_name = ?
            ORDER BY
                CASE
                    WHEN role = ? THEN 0
                    WHEN role = ? THEN 1
                    WHEN role = ? THEN 2
                    ELSE 3
                END,
                id ASC
            LIMIT 1
            """,
            (full_name, ROLE_CLIENT, ROLE_MANAGER, ROLE_ADMIN),
        ).fetchone()
        return row["id"] if row else None

    def _distinct_values(
        self,
        connection: sqlite3.Connection,
        column_name: str,
    ) -> list[str]:
        rows = connection.execute(
            f"""
            SELECT DISTINCT {column_name} AS value
            FROM products
            WHERE {column_name} <> ''
            ORDER BY value COLLATE NOCASE ASC
            """
        ).fetchall()
        return [row["value"] for row in rows]
