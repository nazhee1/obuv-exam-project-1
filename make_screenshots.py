
from __future__ import annotations

import subprocess
from pathlib import Path

from app import ShoeStoreApp, ProductEditorWindow
from repository import get_user_by_credentials

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "docs" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

app = ShoeStoreApp()
app.geometry("1220x760+20+20")


def capture(name: str):
    app.update_idletasks()
    app.update()
    subprocess.run(["scrot", str(OUT_DIR / name)], check=True)


def stage_login():
    capture("01_login.png")
    app.after(400, stage_guest)


def stage_guest():
    app.login(None)
    capture("02_guest_products.png")
    app.after(400, stage_manager)


def stage_manager():
    user = get_user_by_credentials("1diph5e@tutanota.com", "8ntwUp")
    app.login(user)
    page = app._container.winfo_children()[0]
    page.search_var.set("Ботинки")
    page.sort_var.set("По убыванию")
    page.refresh_products()
    capture("03_manager_products.png")
    app.after(400, stage_orders)


def stage_orders():
    app.show_orders_page()
    capture("04_orders.png")
    app.after(400, stage_admin)


def stage_admin():
    user = get_user_by_credentials("94d5ous@gmail.com", "uzWC67")
    app.login(user)
    page = app._container.winfo_children()[0]
    page.open_create_form()
    editor = app.editor_window
    editor.fields["article"].insert(0, "NEW31")
    editor.fields["name"].insert(0, "Кеды")
    editor.fields["category"].set("Женская обувь")
    editor.fields["manufacturer"].set("Kari")
    editor.fields["supplier"].set("Kari")
    editor.fields["unit"].set("шт.")
    editor.fields["price"].insert(0, "2999")
    editor.fields["discount_percent"].insert(0, "10")
    editor.fields["stock_quantity"].insert(0, "4")
    editor.fields["description"].insert("1.0", "Тестовое заполнение формы товара.")
    capture("05_editor.png")
    app.after(400, app.destroy)


app.after(700, stage_login)
app.mainloop()
