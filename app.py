
from __future__ import annotations

import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.font import Font

from PIL import Image, ImageTk

from init_db import main as initialize_database
from repository import (
    User,
    fetch_editor_choices,
    fetch_filters,
    fetch_order,
    fetch_order_editor_choices,
    fetch_orders,
    fetch_product,
    fetch_products,
    get_user_by_credentials,
    next_order_id,
    next_product_id,
)
from services import (
    import_selected_image,
    remove_order,
    remove_product,
    save_order_with_validation,
    save_product_with_validation,
)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGE = BASE_DIR / "resources" / "images" / "picture.png"
APP_ICON = BASE_DIR / "resources" / "images" / "Icon.ico"
LOGO_IMAGE = BASE_DIR / "resources" / "images" / "Icon.png"

WHITE = "#FFFFFF"
GREEN = "#7FFF00"
ACCENT = "#00FA9A"
DISCOUNT_BG = "#2E8B57"
OUT_OF_STOCK = "#87CEEB"


class ShoeStoreApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ООО «Обувь» — вход")
        self.geometry("1240x780")
        self.minsize(1120, 700)
        self.configure(bg=WHITE)
        self.current_user: User | None = None
        self.editor_window: ProductEditorWindow | None = None
        self.order_editor_window: OrderEditorWindow | None = None
        self.images_cache: dict[str, ImageTk.PhotoImage] = {}
        self.option_add("*Font", ("Times New Roman", 11))
        try:
            self.iconbitmap(APP_ICON)
        except Exception:
            pass
        self._container = tk.Frame(self, bg=WHITE)
        self._container.pack(fill="both", expand=True)
        self.show_login_page()

    def clear_container(self) -> None:
        for child in self._container.winfo_children():
            child.destroy()

    def show_login_page(self) -> None:
        self.current_user = None
        self.title("ООО «Обувь» — вход")
        self.clear_container()
        LoginPage(self._container, self).pack(fill="both", expand=True)

    def login(self, user: User | None) -> None:
        self.current_user = user
        self.show_product_page()

    def show_product_page(self) -> None:
        self.title("ООО «Обувь» — товары")
        self.clear_container()
        ProductListPage(self._container, self).pack(fill="both", expand=True)

    def show_orders_page(self) -> None:
        self.title("ООО «Обувь» — заказы")
        self.clear_container()
        OrdersPage(self._container, self).pack(fill="both", expand=True)


class HeaderBar(tk.Frame):
    def __init__(
        self,
        master,
        app: ShoeStoreApp,
        title: str,
        *,
        show_back_button: bool = False,
        show_orders_button: bool = False,
    ):
        super().__init__(master, bg=ACCENT, padx=16, pady=12)
        left = tk.Frame(self, bg=ACCENT)
        left.pack(side="left", fill="y")

        if show_back_button:
            tk.Button(
                left,
                text="Назад",
                command=app.show_product_page,
                bg=GREEN,
                relief="groove",
                padx=10,
            ).pack(side="left", padx=(0, 12))

        tk.Label(
            left,
            text=title,
            bg=ACCENT,
            fg="black",
            font=("Times New Roman", 18, "bold"),
        ).pack(side="left")

        right = tk.Frame(self, bg=ACCENT)
        right.pack(side="right")

        user_name = app.current_user.full_name if app.current_user else "Гость"
        tk.Label(
            right,
            text=user_name,
            bg=GREEN,
            fg="black",
            font=("Times New Roman", 12, "bold"),
            padx=12,
            pady=6,
        ).pack(side="right", padx=(12, 0))
        tk.Button(
            right,
            text="Выйти",
            command=app.show_login_page,
            bg=WHITE,
            relief="groove",
            padx=10,
        ).pack(side="right")

        if show_orders_button:
            tk.Button(
                right,
                text="Заказы",
                command=app.show_orders_page,
                bg=WHITE,
                relief="groove",
                padx=10,
            ).pack(side="right", padx=(0, 8))


class LoginPage(tk.Frame):
    def __init__(self, master, app: ShoeStoreApp):
        super().__init__(master, bg=WHITE)
        self.app = app
        wrapper = tk.Frame(self, bg=WHITE)
        wrapper.pack(expand=True)

        if LOGO_IMAGE.exists():
            logo_image = Image.open(LOGO_IMAGE)
            logo_image.thumbnail((180, 180))
            self.logo = ImageTk.PhotoImage(logo_image)
            tk.Label(wrapper, image=self.logo, bg=WHITE).pack(pady=(0, 12))

        tk.Label(
            wrapper,
            text="ООО «Обувь»",
            bg=WHITE,
            font=("Times New Roman", 24, "bold"),
        ).pack(pady=(0, 8))
        tk.Label(
            wrapper,
            text="Вход в систему учёта товаров и заказов",
            bg=WHITE,
            font=("Times New Roman", 12),
        ).pack(pady=(0, 18))

        form = tk.Frame(wrapper, bg=WHITE)
        form.pack()

        tk.Label(form, text="Логин", bg=WHITE).grid(row=0, column=0, sticky="w", pady=6)
        self.login_entry = tk.Entry(form, width=32)
        self.login_entry.grid(row=1, column=0, pady=(0, 10))

        tk.Label(form, text="Пароль", bg=WHITE).grid(row=2, column=0, sticky="w", pady=6)
        self.password_entry = tk.Entry(form, show="*", width=32)
        self.password_entry.grid(row=3, column=0, pady=(0, 12))

        buttons = tk.Frame(wrapper, bg=WHITE)
        buttons.pack(pady=12)
        tk.Button(buttons, text="Войти", bg=ACCENT, width=20, command=self._login).pack(side="left", padx=8)
        tk.Button(buttons, text="Продолжить как гость", bg=GREEN, width=20, command=lambda: app.login(None)).pack(
            side="left",
            padx=8,
        )

        self.login_entry.bind("<Return>", lambda _: self._login())
        self.password_entry.bind("<Return>", lambda _: self._login())
        self.login_entry.focus_set()

    def _login(self) -> None:
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль.")
            return

        user = get_user_by_credentials(login, password)
        if user is None:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")
            return

        self.app.login(user)


class ScrollableFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=WHITE)
        self.canvas = tk.Canvas(self, bg=WHITE, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=WHITE)

        self.inner.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.window_id, width=event.width),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


class ProductListPage(tk.Frame):
    def __init__(self, master, app: ShoeStoreApp):
        super().__init__(master, bg=WHITE)
        self.app = app
        self.role = app.current_user.role if app.current_user else "Гость"
        show_orders = self.role in {"Менеджер", "Администратор"}

        HeaderBar(self, app, "Список товаров", show_orders_button=show_orders).pack(fill="x")

        controls = tk.Frame(self, bg=WHITE, padx=16, pady=12)
        controls.pack(fill="x")
        self.search_var = tk.StringVar()
        self.supplier_var = tk.StringVar(value="Все поставщики")
        self.sort_var = tk.StringVar(value="Без сортировки")

        if self.role in {"Менеджер", "Администратор"}:
            filters = fetch_filters()

            tk.Label(controls, text="Поиск по всем текстовым полям", bg=WHITE).grid(row=0, column=0, sticky="w")
            search_entry = tk.Entry(controls, textvariable=self.search_var, width=32)
            search_entry.grid(row=1, column=0, padx=(0, 12))
            search_entry.bind("<KeyRelease>", lambda _: self.refresh_products())

            tk.Label(controls, text="Поставщик", bg=WHITE).grid(row=0, column=1, sticky="w")
            supplier_box = ttk.Combobox(
                controls,
                textvariable=self.supplier_var,
                values=["Все поставщики"] + filters["suppliers"],
                width=24,
                state="readonly",
            )
            supplier_box.grid(row=1, column=1, padx=(0, 12))
            supplier_box.bind("<<ComboboxSelected>>", lambda _: self.refresh_products())

            tk.Label(controls, text="Сортировка по количеству на складе", bg=WHITE).grid(row=0, column=2, sticky="w")
            sort_box = ttk.Combobox(
                controls,
                textvariable=self.sort_var,
                values=["Без сортировки", "По возрастанию", "По убыванию"],
                width=22,
                state="readonly",
            )
            sort_box.grid(row=1, column=2, padx=(0, 12))
            sort_box.bind("<<ComboboxSelected>>", lambda _: self.refresh_products())

            tk.Button(controls, text="Сбросить", bg=GREEN, command=self.reset_filters).grid(row=1, column=3, padx=4)

            if self.role == "Администратор":
                tk.Button(controls, text="Добавить товар", bg=ACCENT, command=self.open_create_form).grid(
                    row=1,
                    column=4,
                    padx=20,
                )

        self.summary_label = tk.Label(self, text="", bg=WHITE, anchor="w", padx=16)
        self.summary_label.pack(fill="x")

        self.scroller = ScrollableFrame(self)
        self.scroller.pack(fill="both", expand=True, padx=16, pady=(4, 16))
        self.refresh_products()

    def reset_filters(self) -> None:
        self.search_var.set("")
        self.supplier_var.set("Все поставщики")
        self.sort_var.set("Без сортировки")
        self.refresh_products()

    def _sort_key(self) -> str:
        if self.sort_var.get() == "По возрастанию":
            return "asc"
        if self.sort_var.get() == "По убыванию":
            return "desc"
        return ""

    def _selected_supplier(self) -> str:
        if self.supplier_var.get() == "Все поставщики":
            return ""
        return self.supplier_var.get().strip()

    def refresh_products(self) -> None:
        for child in self.scroller.inner.winfo_children():
            child.destroy()

        allow_filters = self.role in {"Менеджер", "Администратор"}
        products = fetch_products(
            search=self.search_var.get() if allow_filters else "",
            supplier=self._selected_supplier() if allow_filters else "",
            sort_direction=self._sort_key() if allow_filters else "",
        )
        self.summary_label.config(text=f"Найдено товаров: {len(products)}")

        for product in products:
            ProductCard(self.scroller.inner, self.app, product, on_change=self.refresh_products).pack(fill="x", pady=8)

    def open_create_form(self) -> None:
        if self.app.editor_window and self.app.editor_window.winfo_exists():
            self.app.editor_window.focus_set()
            messagebox.showinfo("Информация", "Нельзя открыть более одного окна редактирования.")
            return
        self.app.editor_window = ProductEditorWindow(self.app, None, on_saved=self.refresh_products)


class ProductCard(tk.Frame):
    def __init__(self, master, app: ShoeStoreApp, product: dict, on_change):
        background = WHITE
        if product["stock_quantity"] == 0:
            background = OUT_OF_STOCK
        elif product["discount_percent"] > 15:
            background = DISCOUNT_BG
        super().__init__(master, bg=background, bd=1, relief="solid", padx=12, pady=12)
        self.app = app
        self.product = product
        self.on_change = on_change

        image_label = tk.Label(self, bg=background)
        image_label.grid(row=0, column=0, rowspan=4, sticky="n")
        image_path = BASE_DIR / (product["image_path"] or "")
        if not image_path.exists():
            image_path = DEFAULT_IMAGE
        image = Image.open(image_path)
        image.thumbnail((130, 90))
        photo = ImageTk.PhotoImage(image)
        app.images_cache[f"{product['article']}_{id(self)}"] = photo
        image_label.config(image=photo)

        info = tk.Frame(self, bg=background)
        info.grid(row=0, column=1, sticky="nsew", padx=16)
        self.columnconfigure(1, weight=1)

        top_line = f"ID: {product['id']} | Артикул: {product['article']} — {product['name']} ({product['category']})"
        tk.Label(info, text=top_line, bg=background, font=("Times New Roman", 14, "bold")).pack(anchor="w")
        tk.Label(
            info,
            text=f"Производитель: {product['manufacturer']} | Поставщик: {product['supplier']} | Ед. изм.: {product['unit']}",
            bg=background,
        ).pack(anchor="w", pady=(6, 0))
        tk.Label(
            info,
            text=f"Описание: {product['description']}",
            bg=background,
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))
        tk.Label(
            info,
            text=f"На складе: {product['stock_quantity']} шт. | Скидка: {product['discount_percent']}%",
            bg=background,
        ).pack(anchor="w", pady=(6, 0))

        price_frame = tk.Frame(info, bg=background)
        price_frame.pack(anchor="w", pady=(8, 0))
        if product["discount_percent"] > 0:
            original_font = Font(family="Times New Roman", size=12, overstrike=1)
            tk.Label(price_frame, text=f"{product['price']:.2f} ₽", fg="red", bg=background, font=original_font).pack(
                side="left"
            )
            final_price = product["price"] * (1 - product["discount_percent"] / 100)
            tk.Label(
                price_frame,
                text=f"  {final_price:.2f} ₽",
                fg="black",
                bg=background,
                font=("Times New Roman", 12, "bold"),
            ).pack(side="left")
        else:
            tk.Label(
                price_frame,
                text=f"{product['price']:.2f} ₽",
                bg=background,
                font=("Times New Roman", 12, "bold"),
            ).pack(side="left")

        role = app.current_user.role if app.current_user else "Гость"
        if role == "Администратор":
            buttons = tk.Frame(self, bg=background)
            buttons.grid(row=0, column=2, sticky="ne")
            tk.Button(buttons, text="Редактировать", bg=ACCENT, command=self.edit_product).pack(fill="x", pady=(0, 8))
            tk.Button(buttons, text="Удалить", bg=GREEN, command=self.delete_product).pack(fill="x")

    def edit_product(self) -> None:
        if self.app.editor_window and self.app.editor_window.winfo_exists():
            self.app.editor_window.focus_set()
            messagebox.showinfo("Информация", "Нельзя открыть более одного окна редактирования.")
            return
        self.app.editor_window = ProductEditorWindow(self.app, self.product["article"], on_saved=self.on_change)

    def delete_product(self) -> None:
        if not messagebox.askyesno("Предупреждение", "Удалить выбранный товар? Операцию нельзя отменить."):
            return
        try:
            remove_product(self.product["article"])
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))
            return
        messagebox.showinfo("Информация", "Товар удалён.")
        self.on_change()


class OrdersPage(tk.Frame):
    def __init__(self, master, app: ShoeStoreApp):
        super().__init__(master, bg=WHITE)
        self.app = app
        self.role = app.current_user.role if app.current_user else "Гость"

        HeaderBar(self, app, "Заказы", show_back_button=True).pack(fill="x")

        controls = tk.Frame(self, bg=WHITE, padx=16, pady=12)
        controls.pack(fill="x")
        if self.role == "Администратор":
            tk.Button(controls, text="Добавить заказ", bg=ACCENT, command=self.open_create_form).pack(side="left")

        self.summary_label = tk.Label(self, text="", bg=WHITE, anchor="w", padx=16)
        self.summary_label.pack(fill="x")

        self.content = ScrollableFrame(self)
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.refresh_orders()

    def refresh_orders(self) -> None:
        for child in self.content.inner.winfo_children():
            child.destroy()

        orders = fetch_orders()
        self.summary_label.config(text=f"Найдено заказов: {len(orders)}")

        for order in orders:
            frame = tk.Frame(self.content.inner, bg=WHITE, bd=1, relief="solid", padx=12, pady=12)
            frame.pack(fill="x", pady=8)

            header = tk.Frame(frame, bg=WHITE)
            header.pack(fill="x")
            tk.Label(
                header,
                text=f"Заказ №{order['id']} | Клиент: {order['customer_name']} | Статус: {order['status_name']}",
                bg=WHITE,
                font=("Times New Roman", 13, "bold"),
            ).pack(side="left", anchor="w")

            if self.role == "Администратор":
                actions = tk.Frame(header, bg=WHITE)
                actions.pack(side="right")
                tk.Button(actions, text="Редактировать", bg=ACCENT, command=lambda oid=order["id"]: self.edit_order(oid)).pack(
                    side="left",
                    padx=6,
                )
                tk.Button(actions, text="Удалить", bg=GREEN, command=lambda oid=order["id"]: self.delete_order(oid)).pack(
                    side="left"
                )

            tk.Label(
                frame,
                text=(
                    f"Дата заказа: {order['order_date']} | Дата доставки: {order['delivery_date']} | "
                    f"Пункт выдачи: {order['address']} | Код: {order['receive_code']}"
                ),
                bg=WHITE,
                wraplength=1050,
                justify="left",
            ).pack(anchor="w", pady=(6, 0))

            items_text = ", ".join(
                f"{item['name']} ({item['product_article']}) x{item['quantity']}"
                for item in order["items"]
            )
            tk.Label(
                frame,
                text=f"Состав заказа: {items_text}",
                bg=WHITE,
                wraplength=1050,
                justify="left",
            ).pack(anchor="w", pady=(6, 0))

    def open_create_form(self) -> None:
        if self.app.order_editor_window and self.app.order_editor_window.winfo_exists():
            self.app.order_editor_window.focus_set()
            messagebox.showinfo("Информация", "Нельзя открыть более одного окна редактирования заказа.")
            return
        self.app.order_editor_window = OrderEditorWindow(self.app, None, on_saved=self.refresh_orders)

    def edit_order(self, order_id: int) -> None:
        if self.app.order_editor_window and self.app.order_editor_window.winfo_exists():
            self.app.order_editor_window.focus_set()
            messagebox.showinfo("Информация", "Нельзя открыть более одного окна редактирования заказа.")
            return
        self.app.order_editor_window = OrderEditorWindow(self.app, order_id, on_saved=self.refresh_orders)

    def delete_order(self, order_id: int) -> None:
        if not messagebox.askyesno("Предупреждение", "Удалить выбранный заказ? Операцию нельзя отменить."):
            return
        remove_order(order_id)
        messagebox.showinfo("Информация", "Заказ удалён.")
        self.refresh_orders()


class ProductEditorWindow(tk.Toplevel):
    def __init__(self, app: ShoeStoreApp, article: str | None, on_saved):
        super().__init__(app)
        self.app = app
        self.article = article
        self.on_saved = on_saved
        self.title("Добавление товара" if article is None else "Редактирование товара")
        self.geometry("780x760")
        self.configure(bg=WHITE)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close)

        self.choices = fetch_editor_choices()
        self.current_data = fetch_product(article) if article else None
        self.selected_file = ""
        self.current_image_path = self.current_data["image_path"] if self.current_data else ""

        body = tk.Frame(self, bg=WHITE, padx=16, pady=16)
        body.pack(fill="both", expand=True)

        self.fields: dict[str, tk.Widget] = {}
        row_cursor = 0

        if self.current_data:
            tk.Label(body, text="ID товара", bg=WHITE).grid(row=row_cursor, column=0, sticky="w", pady=6)
            product_id_entry = tk.Entry(body, width=45)
            product_id_entry.grid(row=row_cursor, column=1, sticky="we", pady=6)
            product_id_entry.insert(0, str(self.current_data["id"]))
            product_id_entry.config(state="readonly")
            self.fields["id"] = product_id_entry
            row_cursor += 1

        field_definitions = [
            ("article", "Артикул", tk.Entry),
            ("name", "Наименование товара", tk.Entry),
            ("category", "Категория товара", ttk.Combobox),
            ("manufacturer", "Производитель", ttk.Combobox),
            ("supplier", "Поставщик", ttk.Combobox),
            ("unit", "Единица измерения", ttk.Combobox),
            ("price", "Цена", tk.Entry),
            ("discount_percent", "Действующая скидка", tk.Entry),
            ("stock_quantity", "Количество на складе", tk.Entry),
        ]

        for key, title, widget_type in field_definitions:
            tk.Label(body, text=title, bg=WHITE).grid(row=row_cursor, column=0, sticky="w", pady=6)
            if widget_type is ttk.Combobox:
                values_map = {
                    "category": self.choices["categories"],
                    "manufacturer": self.choices["manufacturers"],
                    "supplier": self.choices["suppliers"],
                    "unit": self.choices["units"],
                }
                widget = ttk.Combobox(body, values=values_map[key], state="readonly", width=42)
            else:
                widget = widget_type(body, width=45)
            widget.grid(row=row_cursor, column=1, sticky="we", pady=6)
            self.fields[key] = widget
            row_cursor += 1

        tk.Label(body, text="Описание товара", bg=WHITE).grid(row=row_cursor, column=0, sticky="nw", pady=6)
        description = tk.Text(body, width=45, height=8)
        description.grid(row=row_cursor, column=1, sticky="we", pady=6)
        self.fields["description"] = description
        row_cursor += 1

        tk.Label(body, text="Изображение", bg=WHITE).grid(row=row_cursor, column=0, sticky="w", pady=6)
        image_row = tk.Frame(body, bg=WHITE)
        image_row.grid(row=row_cursor, column=1, sticky="w", pady=6)
        self.image_label = tk.Label(image_row, text="Файл не выбран", bg=WHITE)
        self.image_label.pack(side="left")
        tk.Button(image_row, text="Выбрать", bg=ACCENT, command=self._select_image).pack(side="left", padx=8)
        row_cursor += 1

        buttons = tk.Frame(body, bg=WHITE)
        buttons.grid(row=row_cursor, column=0, columnspan=2, pady=20)
        tk.Button(buttons, text="Сохранить", bg=ACCENT, width=18, command=self._save).pack(side="left", padx=8)
        tk.Button(buttons, text="Отмена", bg=GREEN, width=18, command=self._close).pack(side="left", padx=8)

        self._fill_form()

    def _fill_form(self) -> None:
        if not self.current_data:
            return
        self.fields["article"].insert(0, self.current_data["article"])
        self.fields["article"].config(state="readonly")
        self.fields["name"].insert(0, self.current_data["name"])
        self.fields["category"].set(self.current_data["category"])
        self.fields["manufacturer"].set(self.current_data["manufacturer"])
        self.fields["supplier"].set(self.current_data["supplier"])
        self.fields["unit"].set(self.current_data["unit"])
        self.fields["price"].insert(0, str(self.current_data["price"]))
        self.fields["discount_percent"].insert(0, str(self.current_data["discount_percent"]))
        self.fields["stock_quantity"].insert(0, str(self.current_data["stock_quantity"]))
        self.fields["description"].insert("1.0", self.current_data["description"])
        self.image_label.config(text=self.current_data["image_path"] or "Файл не выбран")

    def _select_image(self) -> None:
        selected = filedialog.askopenfilename(
            title="Выберите изображение товара",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif")],
        )
        if selected:
            self.selected_file = selected
            self.image_label.config(text=Path(selected).name)

    def _collect_payload(self) -> dict:
        article_value = self.fields["article"].get().strip()
        payload = {
            "id": self.current_data["id"] if self.current_data else next_product_id(),
            "article": article_value,
            "name": self.fields["name"].get().strip(),
            "category": self.fields["category"].get().strip(),
            "manufacturer": self.fields["manufacturer"].get().strip(),
            "supplier": self.fields["supplier"].get().strip(),
            "unit": self.fields["unit"].get().strip(),
            "price": self.fields["price"].get().strip(),
            "discount_percent": self.fields["discount_percent"].get().strip(),
            "stock_quantity": self.fields["stock_quantity"].get().strip(),
            "description": self.fields["description"].get("1.0", "end").strip(),
            "image_path": self.current_image_path,
        }
        if not self.current_data and not article_value:
            payload["article"] = f"ART-{payload['id']:04d}"
        return payload

    def _save(self) -> None:
        payload = self._collect_payload()
        try:
            payload["image_path"] = import_selected_image(
                self.selected_file,
                payload["article"],
                self.current_image_path,
            )
            save_product_with_validation(payload)
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))
            return
        messagebox.showinfo("Информация", "Товар успешно сохранён.")
        self.on_saved()
        self._close()

    def _close(self) -> None:
        self.app.editor_window = None
        self.destroy()


class OrderItemRow(tk.Frame):
    def __init__(self, master, product_values: list[str], on_remove, article: str = "", quantity: str = "1"):
        super().__init__(master, bg=WHITE)
        self.on_remove = on_remove
        self.product_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value=quantity)

        self.product_box = ttk.Combobox(self, textvariable=self.product_var, values=product_values, state="readonly", width=44)
        self.product_box.grid(row=0, column=0, padx=(0, 8))
        if article:
            for value in product_values:
                if value.startswith(f"{article} "):
                    self.product_var.set(value)
                    break

        self.quantity_entry = tk.Entry(self, textvariable=self.quantity_var, width=10)
        self.quantity_entry.grid(row=0, column=1, padx=(0, 8))
        tk.Button(self, text="Удалить", bg=GREEN, command=self._remove).grid(row=0, column=2)

    def _remove(self) -> None:
        self.on_remove(self)

    def get_payload(self) -> dict:
        product_value = self.product_var.get().strip()
        article = product_value.split(" — ")[0].strip() if product_value else ""
        return {
            "article": article,
            "quantity": self.quantity_var.get().strip(),
        }


class OrderEditorWindow(tk.Toplevel):
    def __init__(self, app: ShoeStoreApp, order_id: int | None, on_saved):
        super().__init__(app)
        self.app = app
        self.order_id = order_id
        self.on_saved = on_saved
        self.title("Добавление заказа" if order_id is None else "Редактирование заказа")
        self.geometry("860x760")
        self.configure(bg=WHITE)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._close)

        self.choices = fetch_order_editor_choices()
        self.current_data = fetch_order(order_id) if order_id is not None else None
        self.fields: dict[str, tk.Widget] = {}
        self.item_rows: list[OrderItemRow] = []

        body = tk.Frame(self, bg=WHITE, padx=16, pady=16)
        body.pack(fill="both", expand=True)

        row_cursor = 0
        tk.Label(body, text="ID заказа", bg=WHITE).grid(row=row_cursor, column=0, sticky="w", pady=6)
        order_id_entry = tk.Entry(body, width=45)
        order_id_entry.grid(row=row_cursor, column=1, sticky="we", pady=6)
        order_id_entry.insert(0, str(self.current_data["id"] if self.current_data else next_order_id()))
        order_id_entry.config(state="readonly")
        self.fields["id"] = order_id_entry
        row_cursor += 1

        field_defs = [
            ("order_date", "Дата заказа (ГГГГ-ММ-ДД)", tk.Entry),
            ("delivery_date", "Дата доставки (ГГГГ-ММ-ДД)", tk.Entry),
            ("pickup_point", "Пункт выдачи", ttk.Combobox),
            ("customer", "Клиент", ttk.Combobox),
            ("receive_code", "Код получения", tk.Entry),
            ("status", "Статус заказа", ttk.Combobox),
        ]

        for key, title, widget_type in field_defs:
            tk.Label(body, text=title, bg=WHITE).grid(row=row_cursor, column=0, sticky="w", pady=6)
            if widget_type is ttk.Combobox:
                values_map = {
                    "pickup_point": self.choices["pickup_points"],
                    "customer": self.choices["customers"],
                    "status": self.choices["statuses"],
                }
                widget = ttk.Combobox(body, values=values_map[key], state="readonly", width=42)
            else:
                widget = widget_type(body, width=45)
            widget.grid(row=row_cursor, column=1, sticky="we", pady=6)
            self.fields[key] = widget
            row_cursor += 1

        items_header = tk.Frame(body, bg=WHITE)
        items_header.grid(row=row_cursor, column=0, columnspan=2, sticky="we", pady=(12, 6))
        tk.Label(items_header, text="Состав заказа", bg=WHITE, font=("Times New Roman", 13, "bold")).pack(side="left")
        tk.Button(items_header, text="Добавить товар", bg=ACCENT, command=self.add_item_row).pack(side="right")
        row_cursor += 1

        self.items_container = tk.Frame(body, bg=WHITE)
        self.items_container.grid(row=row_cursor, column=0, columnspan=2, sticky="we")
        row_cursor += 1

        buttons = tk.Frame(body, bg=WHITE)
        buttons.grid(row=row_cursor, column=0, columnspan=2, pady=20)
        tk.Button(buttons, text="Сохранить", bg=ACCENT, width=18, command=self._save).pack(side="left", padx=8)
        tk.Button(buttons, text="Отмена", bg=GREEN, width=18, command=self._close).pack(side="left", padx=8)

        self._fill_form()

    def _fill_form(self) -> None:
        if self.current_data:
            self.fields["order_date"].insert(0, self.current_data["order_date"])
            self.fields["delivery_date"].insert(0, self.current_data["delivery_date"])
            self.fields["pickup_point"].set(self.current_data["address"])
            self.fields["customer"].set(self.current_data["customer_name"])
            self.fields["receive_code"].insert(0, str(self.current_data["receive_code"]))
            self.fields["status"].set(self.current_data["status_name"])

            for item in self.current_data["items"]:
                self.add_item_row(article=item["product_article"], quantity=str(item["quantity"]))
        else:
            today = date.today().isoformat()
            self.fields["order_date"].insert(0, today)
            self.fields["delivery_date"].insert(0, today)
            if self.choices["pickup_points"]:
                self.fields["pickup_point"].set(self.choices["pickup_points"][0])
            if self.choices["customers"]:
                self.fields["customer"].set(self.choices["customers"][0])
            if self.choices["statuses"]:
                self.fields["status"].set(self.choices["statuses"][0])
            self.fields["receive_code"].insert(0, "1000")
            self.add_item_row()

    def add_item_row(self, *, article: str = "", quantity: str = "1") -> None:
        row = OrderItemRow(
            self.items_container,
            self.choices["products"],
            self.remove_item_row,
            article=article,
            quantity=quantity,
        )
        row.pack(anchor="w", pady=4)
        self.item_rows.append(row)

    def remove_item_row(self, row: OrderItemRow) -> None:
        if len(self.item_rows) == 1:
            messagebox.showwarning("Предупреждение", "В заказе должен остаться хотя бы один товар.")
            return
        self.item_rows.remove(row)
        row.destroy()

    def _collect_payload(self) -> dict:
        return {
            "id": self.fields["id"].get().strip(),
            "order_date": self.fields["order_date"].get().strip(),
            "delivery_date": self.fields["delivery_date"].get().strip(),
            "pickup_point": self.fields["pickup_point"].get().strip(),
            "customer": self.fields["customer"].get().strip(),
            "receive_code": self.fields["receive_code"].get().strip(),
            "status": self.fields["status"].get().strip(),
            "items": [row.get_payload() for row in self.item_rows],
        }

    def _save(self) -> None:
        payload = self._collect_payload()
        try:
            save_order_with_validation(payload)
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))
            return
        messagebox.showinfo("Информация", "Заказ успешно сохранён.")
        self.on_saved()
        self._close()

    def _close(self) -> None:
        self.app.order_editor_window = None
        self.destroy()


def ensure_database() -> None:
    if not (BASE_DIR / "db.sqlite3").exists():
        initialize_database()


if __name__ == "__main__":
    ensure_database()
    app = ShoeStoreApp()
    app.mainloop()
