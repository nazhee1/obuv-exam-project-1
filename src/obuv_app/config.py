from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = APP_ROOT / "data"
DB_PATH = DATA_DIR / "obuv.sqlite3"
DUMP_PATH = APP_ROOT / "dump.sql"

IMPORTS_DIR = APP_ROOT / "resources" / "imports"
PRODUCTS_XLSX = IMPORTS_DIR / "products.xlsx"
USERS_XLSX = IMPORTS_DIR / "users.xlsx"
ORDERS_XLSX = IMPORTS_DIR / "orders.xlsx"
PICKUP_POINTS_XLSX = IMPORTS_DIR / "pickup_points.xlsx"

ASSETS_DIR = APP_ROOT / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"
LOGO_PATH = ASSETS_DIR / "icon.png"
PRODUCT_IMAGES_DIR = ASSETS_DIR / "products"

ROLE_GUEST = "Гость"
ROLE_CLIENT = "Авторизированный клиент"
ROLE_MANAGER = "Менеджер"
ROLE_ADMIN = "Администратор"

ADVANCED_ROLES = {ROLE_MANAGER, ROLE_ADMIN}
MANAGER_ROLES = {ROLE_MANAGER, ROLE_ADMIN}

ORDER_STATUSES = [
    "Новый",
    "Собирается",
    "В пути",
    "Готов к выдаче",
    "Завершен",
    "Отменен",
]

SORT_OPTIONS = {
    "name_asc": "Наименование: А-Я",
    "name_desc": "Наименование: Я-А",
    "price_asc": "Цена: по возрастанию",
    "price_desc": "Цена: по убыванию",
    "discount_desc": "Скидка: сначала большая",
    "stock_desc": "Остаток: сначала большой",
}

THEME = {
    "background": "#FFFFFF",
    "surface": "#FFFFFF",
    "surface_alt": "#7FFF00",
    "accent": "#00FA9A",
    "discount_highlight": "#2E8B57",
    "border": "#8BC34A",
    "text": "#1E1E1E",
    "muted": "#5E5E5E",
}
