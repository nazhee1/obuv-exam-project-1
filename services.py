
from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from PIL import Image

from repository import delete_order, delete_product, product_used_in_orders, save_order, save_product

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "data" / "product_images"

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}


def validate_product_payload(payload: dict) -> None:
    required = {
        "article": "Артикул",
        "name": "Наименование товара",
        "unit": "Единица измерения",
        "price": "Цена",
        "supplier": "Поставщик",
        "manufacturer": "Производитель",
        "category": "Категория товара",
        "discount_percent": "Действующая скидка",
        "stock_quantity": "Количество на складе",
        "description": "Описание товара",
    }
    for key, title in required.items():
        if str(payload.get(key, "")).strip() == "":
            raise ValueError(f"Поле «{title}» обязательно для заполнения.")

    try:
        price = float(payload["price"])
    except ValueError as error:
        raise ValueError("Цена должна быть числом.") from error

    try:
        stock_quantity = int(payload["stock_quantity"])
    except ValueError as error:
        raise ValueError("Количество на складе должно быть целым числом.") from error

    try:
        discount = int(payload["discount_percent"])
    except ValueError as error:
        raise ValueError("Скидка должна быть целым числом.") from error

    if price < 0:
        raise ValueError("Цена не может быть отрицательной.")
    if stock_quantity < 0:
        raise ValueError("Количество на складе не может быть отрицательным.")
    if discount < 0 or discount > 100:
        raise ValueError("Скидка должна быть в диапазоне от 0 до 100.")


def validate_order_payload(payload: dict) -> None:
    required = {
        "order_date": "Дата заказа",
        "delivery_date": "Дата доставки",
        "pickup_point": "Пункт выдачи",
        "customer": "Клиент",
        "receive_code": "Код получения",
        "status": "Статус заказа",
    }
    for key, title in required.items():
        if str(payload.get(key, "")).strip() == "":
            raise ValueError(f"Поле «{title}» обязательно для заполнения.")

    try:
        date.fromisoformat(str(payload["order_date"]).strip())
    except ValueError as error:
        raise ValueError("Дата заказа должна быть в формате ГГГГ-ММ-ДД.") from error

    try:
        date.fromisoformat(str(payload["delivery_date"]).strip())
    except ValueError as error:
        raise ValueError("Дата доставки должна быть в формате ГГГГ-ММ-ДД.") from error

    try:
        receive_code = int(str(payload["receive_code"]).strip())
    except ValueError as error:
        raise ValueError("Код получения должен быть целым числом.") from error

    if receive_code < 0:
        raise ValueError("Код получения не может быть отрицательным.")

    items = payload.get("items") or []
    if not items:
        raise ValueError("В заказе должен быть хотя бы один товар.")

    for index, item in enumerate(items, start=1):
        article = str(item.get("article", "")).strip()
        quantity_raw = str(item.get("quantity", "")).strip()
        if not article:
            raise ValueError(f"В строке {index} не выбран товар.")
        try:
            quantity = int(quantity_raw)
        except ValueError as error:
            raise ValueError(f"Количество в строке {index} должно быть целым числом.") from error
        if quantity <= 0:
            raise ValueError(f"Количество в строке {index} должно быть больше нуля.")


def import_selected_image(source_path: str, article: str, previous_path: str = "") -> str:
    if not source_path:
        return previous_path
    source = Path(source_path)
    if source.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Поддерживаются только изображения PNG, JPG, JPEG, BMP и GIF.")
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        if image.width > 300 or image.height > 200:
            raise ValueError("Размер изображения не должен превышать 300x200 пикселей.")
    target_name = f"{article}{source.suffix.lower()}"
    target_path = IMAGE_DIR / target_name
    if previous_path:
        previous_file = BASE_DIR / previous_path
        if previous_file.exists() and previous_file != target_path:
            previous_file.unlink()
    shutil.copy2(source, target_path)
    return target_path.relative_to(BASE_DIR).as_posix()


def save_product_with_validation(payload: dict) -> None:
    validate_product_payload(payload)
    save_product(payload)


def save_order_with_validation(payload: dict) -> None:
    validate_order_payload(payload)
    save_order(payload)


def remove_product(article: str) -> None:
    if product_used_in_orders(article):
        raise ValueError("Товар нельзя удалить, потому что он присутствует в заказах.")
    delete_product(article)


def remove_order(order_id: int) -> None:
    delete_order(order_id)
