
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from database import connect


@dataclass
class User:
    id: int
    full_name: str
    login: str
    role: str


def get_user_by_credentials(login: str, password: str) -> User | None:
    query = """
        SELECT user.id, user.full_name, user.login, role.name AS role
        FROM user
        JOIN role ON role.id = user.role_id
        WHERE user.login = ? AND user.password = ?
    """
    with connect() as connection:
        row = connection.execute(query, (login, password)).fetchone()
    if row is None:
        return None
    return User(id=row["id"], full_name=row["full_name"], login=row["login"], role=row["role"])


def fetch_filters() -> dict[str, list[str]]:
    with connect() as connection:
        suppliers = [
            row["name"]
            for row in connection.execute("SELECT name FROM supplier ORDER BY name")
        ]
    return {"suppliers": suppliers}


def fetch_products(search: str = "", supplier: str = "", sort_direction: str = "") -> list[dict]:
    filters: list[str] = []
    params: list[object] = []

    if search.strip():
        filters.append(
            "("
            "CAST(product.id AS TEXT) LIKE ? OR product.article LIKE ? OR product.name LIKE ? OR "
            "category.name LIKE ? OR manufacturer.name LIKE ? OR supplier.name LIKE ? OR "
            "unit.name LIKE ? OR product.description LIKE ?"
            ")"
        )
        like_value = f"%{search.strip()}%"
        params.extend([like_value] * 8)

    if supplier.strip():
        filters.append("supplier.name = ?")
        params.append(supplier.strip())

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    order_clause = "ORDER BY product.name ASC"
    if sort_direction == "asc":
        order_clause = "ORDER BY product.stock_quantity ASC, product.name ASC"
    elif sort_direction == "desc":
        order_clause = "ORDER BY product.stock_quantity DESC, product.name ASC"

    query = f"""
        SELECT
            product.id,
            product.article,
            product.name,
            unit.name AS unit,
            product.price,
            supplier.name AS supplier,
            manufacturer.name AS manufacturer,
            category.name AS category,
            product.discount_percent,
            product.stock_quantity,
            product.description,
            product.image_path
        FROM product
        JOIN unit ON unit.id = product.unit_id
        JOIN supplier ON supplier.id = product.supplier_id
        JOIN manufacturer ON manufacturer.id = product.manufacturer_id
        JOIN category ON category.id = product.category_id
        {where_clause}
        {order_clause}
    """
    with connect() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def fetch_orders() -> list[dict]:
    query = """
        SELECT
            customer_order.id,
            customer_order.order_date,
            customer_order.delivery_date,
            pickup_point.address,
            user.full_name AS customer_name,
            customer_order.receive_code,
            order_status.name AS status_name
        FROM customer_order
        JOIN pickup_point ON pickup_point.id = customer_order.pickup_point_id
        JOIN user ON user.id = customer_order.customer_id
        JOIN order_status ON order_status.id = customer_order.status_id
        ORDER BY customer_order.id
    """
    with connect() as connection:
        orders = []
        for row in connection.execute(query).fetchall():
            items = connection.execute(
                """
                SELECT order_item.product_article, order_item.quantity, product.name
                FROM order_item
                JOIN product ON product.article = order_item.product_article
                WHERE order_item.order_id = ?
                ORDER BY order_item.id
                """,
                (row["id"],),
            ).fetchall()
            payload = dict(row)
            payload["items"] = [dict(item) for item in items]
            orders.append(payload)
    return orders


def fetch_order(order_id: int) -> dict | None:
    query = """
        SELECT
            customer_order.id,
            customer_order.order_date,
            customer_order.delivery_date,
            pickup_point.address,
            user.full_name AS customer_name,
            customer_order.receive_code,
            order_status.name AS status_name
        FROM customer_order
        JOIN pickup_point ON pickup_point.id = customer_order.pickup_point_id
        JOIN user ON user.id = customer_order.customer_id
        JOIN order_status ON order_status.id = customer_order.status_id
        WHERE customer_order.id = ?
    """
    with connect() as connection:
        row = connection.execute(query, (order_id,)).fetchone()
        if row is None:
            return None
        items = connection.execute(
            """
            SELECT order_item.product_article, order_item.quantity, product.name
            FROM order_item
            JOIN product ON product.article = order_item.product_article
            WHERE order_item.order_id = ?
            ORDER BY order_item.id
            """,
            (order_id,),
        ).fetchall()
    payload = dict(row)
    payload["items"] = [dict(item) for item in items]
    return payload


def fetch_product(article: str) -> dict | None:
    query = """
        SELECT
            product.id,
            product.article,
            product.name,
            unit.name AS unit,
            product.price,
            supplier.name AS supplier,
            manufacturer.name AS manufacturer,
            category.name AS category,
            product.discount_percent,
            product.stock_quantity,
            product.description,
            product.image_path
        FROM product
        JOIN unit ON unit.id = product.unit_id
        JOIN supplier ON supplier.id = product.supplier_id
        JOIN manufacturer ON manufacturer.id = product.manufacturer_id
        JOIN category ON category.id = product.category_id
        WHERE product.article = ?
    """
    with connect() as connection:
        row = connection.execute(query, (article,)).fetchone()
    return dict(row) if row else None


def fetch_editor_choices() -> dict[str, list[str]]:
    with connect() as connection:
        return {
            "categories": [row["name"] for row in connection.execute("SELECT name FROM category ORDER BY name")],
            "manufacturers": [row["name"] for row in connection.execute("SELECT name FROM manufacturer ORDER BY name")],
            "suppliers": [row["name"] for row in connection.execute("SELECT name FROM supplier ORDER BY name")],
            "units": [row["name"] for row in connection.execute("SELECT name FROM unit ORDER BY name")],
        }


def fetch_order_editor_choices() -> dict[str, list[str]]:
    with connect() as connection:
        return {
            "pickup_points": [row["address"] for row in connection.execute("SELECT address FROM pickup_point ORDER BY address")],
            "customers": [row["full_name"] for row in connection.execute("SELECT full_name FROM user ORDER BY full_name")],
            "statuses": [row["name"] for row in connection.execute("SELECT name FROM order_status ORDER BY id")],
            "products": [
                f"{row['article']} — {row['name']}"
                for row in connection.execute("SELECT article, name FROM product ORDER BY name, article")
            ],
        }


def next_product_id() -> int:
    with connect() as connection:
        row = connection.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM product").fetchone()
    return int(row["next_id"])


def next_order_id() -> int:
    with connect() as connection:
        row = connection.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM customer_order").fetchone()
    return int(row["next_id"])


def product_used_in_orders(article: str) -> bool:
    with connect() as connection:
        row = connection.execute(
            "SELECT 1 FROM order_item WHERE product_article = ? LIMIT 1",
            (article,),
        ).fetchone()
    return row is not None


def _lookup_id(connection, table: str, name: str, field: str = "name") -> int:
    row = connection.execute(f"SELECT id FROM {table} WHERE {field} = ?", (name,)).fetchone()
    if row is None:
        raise ValueError(f"Не найдено значение {name!r} в таблице {table}.")
    return int(row["id"])


def save_product(data: dict) -> None:
    with connect() as connection:
        payload = {
            "article": data["article"].strip(),
            "name": data["name"].strip(),
            "unit_id": _lookup_id(connection, "unit", data["unit"]),
            "price": float(data["price"]),
            "supplier_id": _lookup_id(connection, "supplier", data["supplier"]),
            "manufacturer_id": _lookup_id(connection, "manufacturer", data["manufacturer"]),
            "category_id": _lookup_id(connection, "category", data["category"]),
            "discount_percent": int(data["discount_percent"]),
            "stock_quantity": int(data["stock_quantity"]),
            "description": data["description"].strip(),
            "image_path": data.get("image_path") or "",
        }
        exists = connection.execute("SELECT id FROM product WHERE article = ?", (payload["article"],)).fetchone()
        if exists:
            connection.execute(
                """
                UPDATE product
                SET
                    name = :name,
                    unit_id = :unit_id,
                    price = :price,
                    supplier_id = :supplier_id,
                    manufacturer_id = :manufacturer_id,
                    category_id = :category_id,
                    discount_percent = :discount_percent,
                    stock_quantity = :stock_quantity,
                    description = :description,
                    image_path = :image_path
                WHERE article = :article
                """,
                payload,
            )
        else:
            connection.execute(
                """
                INSERT INTO product (
                    article, name, unit_id, price, supplier_id, manufacturer_id, category_id,
                    discount_percent, stock_quantity, description, image_path
                ) VALUES (
                    :article, :name, :unit_id, :price, :supplier_id, :manufacturer_id, :category_id,
                    :discount_percent, :stock_quantity, :description, :image_path
                )
                """,
                payload,
            )
        connection.commit()


def save_order(data: dict) -> None:
    with connect() as connection:
        payload = {
            "id": int(data["id"]),
            "order_date": data["order_date"],
            "delivery_date": data["delivery_date"],
            "pickup_point_id": _lookup_id(connection, "pickup_point", data["pickup_point"], field="address"),
            "customer_id": _lookup_id(connection, "user", data["customer"], field="full_name"),
            "receive_code": int(data["receive_code"]),
            "status_id": _lookup_id(connection, "order_status", data["status"]),
        }
        exists = connection.execute("SELECT 1 FROM customer_order WHERE id = ?", (payload["id"],)).fetchone()
        if exists:
            connection.execute(
                """
                UPDATE customer_order
                SET
                    order_date = :order_date,
                    delivery_date = :delivery_date,
                    pickup_point_id = :pickup_point_id,
                    customer_id = :customer_id,
                    receive_code = :receive_code,
                    status_id = :status_id
                WHERE id = :id
                """,
                payload,
            )
            connection.execute("DELETE FROM order_item WHERE order_id = ?", (payload["id"],))
        else:
            connection.execute(
                """
                INSERT INTO customer_order(
                    id, order_date, delivery_date, pickup_point_id, customer_id, receive_code, status_id
                ) VALUES (
                    :id, :order_date, :delivery_date, :pickup_point_id, :customer_id, :receive_code, :status_id
                )
                """,
                payload,
            )

        for item in data["items"]:
            connection.execute(
                """
                INSERT INTO order_item(order_id, product_article, quantity)
                VALUES (?, ?, ?)
                """,
                (payload["id"], item["article"], int(item["quantity"])),
            )
        connection.commit()


def delete_product(article: str) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM product WHERE article = ?", (article,))
        connection.commit()


def delete_order(order_id: int) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM customer_order WHERE id = ?", (order_id,))
        connection.commit()
