from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable

from .config import (
    DUMP_PATH,
    ICON_PATH,
    LOGO_PATH,
    MANAGER_ROLES,
    ORDER_STATUSES,
    PRODUCT_IMAGES_DIR,
    ROLE_ADMIN,
    ROLE_GUEST,
    SORT_OPTIONS,
    THEME,
)
from .database import DatabaseManager


def format_money(value: float) -> str:
    return f"{value:,.2f} руб.".replace(",", " ").replace(".00", "")


def launch_app() -> None:
    app = ObuvApplication()
    app.mainloop()


class ObuvApplication(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.db = DatabaseManager()
        self.db.initialize()

        self.title("ООО «Обувь»")
        self.geometry("1360x860")
        self.minsize(1120, 720)
        self.configure(bg=THEME["background"])
        self.current_view: tk.Widget | None = None
        self.logo_image: tk.PhotoImage | None = self._load_logo()

        self._configure_styles()
        self._set_icon()
        self.show_login()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        default_font = ("Times New Roman", 11)
        heading_font = ("Times New Roman", 12, "bold")
        title_font = ("Times New Roman", 14, "bold")

        style.configure(".", font=default_font)
        style.configure("TFrame", background=THEME["background"])
        style.configure("TLabel", background=THEME["background"], foreground=THEME["text"])
        style.configure(
            "Title.TLabel",
            background=THEME["background"],
            foreground=THEME["text"],
            font=title_font,
        )
        style.configure(
            "Accent.TButton",
            background=THEME["accent"],
            foreground=THEME["text"],
            bordercolor=THEME["border"],
            focusthickness=3,
            focuscolor=THEME["accent"],
        )
        style.map(
            "Accent.TButton",
            background=[("active", THEME["surface_alt"])],
        )
        style.configure(
            "Treeview",
            font=default_font,
            rowheight=28,
            background=THEME["surface"],
            fieldbackground=THEME["surface"],
            foreground=THEME["text"],
        )
        style.configure(
            "Treeview.Heading",
            font=heading_font,
            background=THEME["surface_alt"],
            foreground=THEME["text"],
        )
        style.configure(
            "TNotebook",
            background=THEME["background"],
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            font=heading_font,
            padding=(14, 8),
            background=THEME["surface_alt"],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", THEME["accent"])],
            expand=[("selected", [1, 1, 1, 0])],
        )

    def _set_icon(self) -> None:
        try:
            self.iconbitmap(default=str(ICON_PATH))
        except tk.TclError:
            pass

    def _load_logo(self) -> tk.PhotoImage | None:
        try:
            image = tk.PhotoImage(file=str(LOGO_PATH))
        except tk.TclError:
            return None
        scale_x = max(1, image.width() // 120)
        scale_y = max(1, image.height() // 120)
        return image.subsample(scale_x, scale_y)

    def show_login(self) -> None:
        self._swap_view(LoginView(self, self.db, self._login, self._login_as_guest))

    def show_main(self, user: dict[str, Any]) -> None:
        self._swap_view(MainView(self, self.db, user, self.show_login))

    def _swap_view(self, widget: tk.Widget) -> None:
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = widget
        self.current_view.pack(fill="both", expand=True)

    def _login(self, login: str, password: str) -> None:
        user = self.db.authenticate(login, password)
        if not user:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")
            return
        self.show_main(user)

    def _login_as_guest(self) -> None:
        self.show_main(
            {
                "id": None,
                "full_name": "Гость",
                "login": "",
                "role": ROLE_GUEST,
            }
        )


class LoginView(ttk.Frame):
    def __init__(
        self,
        master: ObuvApplication,
        db: DatabaseManager,
        on_login: Callable[[str, str], None],
        on_guest_login: Callable[[], None],
    ) -> None:
        super().__init__(master, padding=24)
        self.master = master
        self.db = db
        self.on_login = on_login
        self.on_guest_login = on_guest_login

        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = tk.Frame(
            self,
            bg=THEME["surface_alt"],
            highlightthickness=2,
            highlightbackground=THEME["border"],
            padx=26,
            pady=26,
        )
        card.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        card.grid_columnconfigure(0, weight=1)

        if master.logo_image is not None:
            logo = tk.Label(card, image=master.logo_image, bg=THEME["surface_alt"])
            logo.grid(row=0, column=0, pady=(0, 8))

        ttk.Label(card, text="ООО «Обувь»", style="Title.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Label(
            card,
            text=(
                "Авторизация обязательна для менеджера, администратора и "
                "авторизированного клиента. Гость видит только каталог товаров "
                "без поиска, фильтров и сортировки."
            ),
            wraplength=760,
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(8, 18))

        form = ttk.Frame(card)
        form.grid(row=3, column=0, sticky="ew")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Логин").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        login_entry = ttk.Entry(form, textvariable=self.login_var, width=46)
        login_entry.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="Пароль").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        password_entry = ttk.Entry(form, textvariable=self.password_var, show="*", width=46)
        password_entry.grid(row=1, column=1, sticky="ew", pady=6)

        actions = ttk.Frame(card)
        actions.grid(row=4, column=0, sticky="w", pady=(16, 16))
        ttk.Button(actions, text="Войти", style="Accent.TButton", command=self._submit).pack(
            side="left"
        )
        ttk.Button(actions, text="Продолжить как гость", command=self.on_guest_login).pack(
            side="left", padx=(10, 0)
        )

        accounts_text = "\n".join(
            f"{item['role']}: {item['login']} / {item['password']}"
            for item in db.get_demo_accounts()
        )
        ttk.Label(
            card,
            text="Тестовые учетные записи:\n" + accounts_text,
            justify="left",
        ).grid(row=5, column=0, sticky="w", pady=(4, 0))

        login_entry.focus_set()
        password_entry.bind("<Return>", lambda _event: self._submit())

    def _submit(self) -> None:
        self.on_login(self.login_var.get(), self.password_var.get())


class MainView(ttk.Frame):
    def __init__(
        self,
        master: ObuvApplication,
        db: DatabaseManager,
        user: dict[str, Any],
        on_logout: Callable[[], None],
    ) -> None:
        super().__init__(master, padding=20)
        self.master = master
        self.db = db
        self.user = user
        self.on_logout = on_logout

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.summary_var = tk.StringVar()

        self._build_header()
        self._build_body()
        self.refresh_summary()

    def _build_header(self) -> None:
        header = tk.Frame(
            self,
            bg=THEME["surface_alt"],
            highlightthickness=2,
            highlightbackground=THEME["border"],
            padx=18,
            pady=14,
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(1, weight=1)

        if self.master.logo_image is not None:
            tk.Label(header, image=self.master.logo_image, bg=THEME["surface_alt"]).grid(
                row=0, column=0, rowspan=2, sticky="nw", padx=(0, 14)
            )

        tk.Label(
            header,
            text="Экзаменационный проект по модулям 1-3",
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            font=("Times New Roman", 16, "bold"),
        ).grid(row=0, column=1, sticky="w")

        tk.Label(
            header,
            text=f"Пользователь: {self.user['full_name']} | Роль: {self.user['role']}",
            bg=THEME["surface_alt"],
            fg=THEME["text"],
            font=("Times New Roman", 11),
        ).grid(row=1, column=1, sticky="w", pady=(4, 0))

        info = ttk.Frame(header)
        info.grid(row=0, column=2, rowspan=2, sticky="e")
        ttk.Label(info, textvariable=self.summary_var).pack(anchor="e")
        ttk.Button(info, text="Сформировать dump.sql", command=self._create_dump).pack(
            anchor="e", pady=(8, 6)
        )
        ttk.Button(info, text="Выйти", command=self.on_logout).pack(anchor="e")

    def _build_body(self) -> None:
        role = self.user["role"]
        if role in MANAGER_ROLES:
            notebook = ttk.Notebook(self)
            notebook.grid(row=1, column=0, sticky="nsew")

            products_tab = ProductCatalogPanel(
                notebook,
                db=self.db,
                role=role,
                on_data_changed=self.refresh_summary,
                advanced_mode=True,
                allow_management=role == ROLE_ADMIN,
            )
            notebook.add(products_tab, text="Товары")

            orders_tab = OrdersPanel(
                notebook,
                db=self.db,
                role=role,
                on_data_changed=self.refresh_summary,
                allow_management=role == ROLE_ADMIN,
            )
            notebook.add(orders_tab, text="Заказы")
        else:
            panel = ProductCatalogPanel(
                self,
                db=self.db,
                role=role,
                on_data_changed=self.refresh_summary,
                advanced_mode=False,
                allow_management=False,
            )
            panel.grid(row=1, column=0, sticky="nsew")

    def refresh_summary(self) -> None:
        summary = self.db.get_summary()
        self.summary_var.set(
            f"Товаров: {summary['products']} | Заказов: {summary['orders']} | Пользователей: {summary['users']}"
        )

    def _create_dump(self) -> None:
        dump_path = self.db.create_dump_file(DUMP_PATH)
        messagebox.showinfo(
            "Готово",
            f"Файл dump.sql сформирован:\n{dump_path}",
        )


class ProductCatalogPanel(ttk.Frame):
    def __init__(
        self,
        master: tk.Widget,
        db: DatabaseManager,
        role: str,
        on_data_changed: Callable[[], None],
        advanced_mode: bool,
        allow_management: bool,
    ) -> None:
        super().__init__(master, padding=12)
        self.db = db
        self.role = role
        self.on_data_changed = on_data_changed
        self.advanced_mode = advanced_mode
        self.allow_management = allow_management

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Все категории")
        self.sort_var = tk.StringVar(value="name_asc")
        self.result_var = tk.StringVar()

        self._build_controls()
        self._build_table()
        self.refresh()

    def _build_controls(self) -> None:
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Каталог товаров", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(frame, textvariable=self.result_var).grid(row=0, column=1, sticky="e")

        if not self.advanced_mode and not self.allow_management:
            ttk.Label(
                frame,
                text=(
                    "Гость и авторизированный клиент видят каталог без "
                    "фильтрации, сортировки и поиска."
                ),
                justify="left",
            ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
            return

        tools = ttk.Frame(frame)
        tools.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        tools.columnconfigure(1, weight=1)

        ttk.Label(tools, text="Поиск").grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Entry(tools, textvariable=self.search_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(tools, text="Категория").grid(row=0, column=2, sticky="w", padx=(12, 6))
        self.category_combo = ttk.Combobox(tools, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=0, column=3, sticky="ew")

        ttk.Label(tools, text="Сортировка").grid(row=0, column=4, sticky="w", padx=(12, 6))
        self.sort_combo = ttk.Combobox(
            tools,
            textvariable=self.sort_var,
            values=list(SORT_OPTIONS.keys()),
            state="readonly",
            width=22,
        )
        self.sort_combo.grid(row=0, column=5, sticky="ew")

        ttk.Button(tools, text="Применить", command=self.refresh).grid(row=0, column=6, padx=(10, 0))
        ttk.Button(tools, text="Сбросить", command=self._reset_filters).grid(
            row=0, column=7, padx=(8, 0)
        )

        if self.allow_management:
            buttons = ttk.Frame(frame)
            buttons.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
            ttk.Button(buttons, text="Добавить товар", command=self._add_product).pack(
                side="left"
            )
            ttk.Button(buttons, text="Редактировать", command=self._edit_product).pack(
                side="left", padx=(8, 0)
            )
            ttk.Button(buttons, text="Удалить", command=self._delete_product).pack(
                side="left", padx=(8, 0)
            )

    def _build_table(self) -> None:
        columns = (
            "article",
            "name",
            "category",
            "manufacturer",
            "price",
            "discount",
            "discount_price",
            "stock",
        )
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", lambda _event: self._show_product_details())

        headings = {
            "article": "Артикул",
            "name": "Наименование",
            "category": "Категория",
            "manufacturer": "Производитель",
            "price": "Цена",
            "discount": "Скидка",
            "discount_price": "Цена со скидкой",
            "stock": "Остаток",
        }
        widths = {
            "article": 120,
            "name": 180,
            "category": 150,
            "manufacturer": 150,
            "price": 110,
            "discount": 90,
            "discount_price": 130,
            "stock": 90,
        }
        for key in columns:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor="center")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.tag_configure("high_discount", background=THEME["discount_highlight"])

    def refresh(self) -> None:
        category = ""
        sort_key = "name_asc"
        search = ""
        if self.advanced_mode:
            category = "" if self.category_var.get() == "Все категории" else self.category_var.get()
            sort_key = self.sort_var.get() or "name_asc"
            search = self.search_var.get()

        products = self.db.list_products(search=search, category=category, sort_key=sort_key)
        self.tree.delete(*self.tree.get_children())
        for product in products:
            tags = ("high_discount",) if product["discount_percent"] > 15 else ()
            self.tree.insert(
                "",
                "end",
                iid=product["article"],
                values=(
                    product["article"],
                    product["name"],
                    product["category"],
                    product["manufacturer"],
                    format_money(product["price"]),
                    f"{product['discount_percent']}%",
                    format_money(product["discount_price"]),
                    product["stock_quantity"],
                ),
                tags=tags,
            )

        if self.advanced_mode:
            categories = ["Все категории"] + self.db.get_product_reference_data()["categories"]
            self.category_combo.configure(values=categories)
            if self.category_var.get() not in categories:
                self.category_var.set("Все категории")
            self.sort_combo.configure(values=list(SORT_OPTIONS.keys()))

        self.result_var.set(f"Найдено товаров: {len(products)}")

    def _reset_filters(self) -> None:
        self.search_var.set("")
        self.category_var.set("Все категории")
        self.sort_var.set("name_asc")
        self.refresh()

    def _selected_article(self) -> str | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return selected[0]

    def _show_product_details(self) -> None:
        article = self._selected_article()
        if not article:
            return
        product = self.db.get_product(article)
        if product:
            ProductDetailsDialog(self, product)

    def _add_product(self) -> None:
        dialog = ProductFormDialog(self, self.db)
        self.wait_window(dialog)
        if dialog.saved:
            self.refresh()
            self.on_data_changed()

    def _edit_product(self) -> None:
        article = self._selected_article()
        if not article:
            messagebox.showwarning("Нет выбора", "Сначала выберите товар.")
            return
        dialog = ProductFormDialog(self, self.db, article=article)
        self.wait_window(dialog)
        if dialog.saved:
            self.refresh()
            self.on_data_changed()

    def _delete_product(self) -> None:
        article = self._selected_article()
        if not article:
            messagebox.showwarning("Нет выбора", "Сначала выберите товар.")
            return
        if not messagebox.askyesno("Подтверждение", f"Удалить товар {article}?"):
            return
        try:
            self.db.delete_product(article)
        except ValueError as exc:
            messagebox.showerror("Ошибка", str(exc))
            return
        self.refresh()
        self.on_data_changed()


class OrdersPanel(ttk.Frame):
    def __init__(
        self,
        master: tk.Widget,
        db: DatabaseManager,
        role: str,
        on_data_changed: Callable[[], None],
        allow_management: bool,
    ) -> None:
        super().__init__(master, padding=12)
        self.db = db
        self.role = role
        self.on_data_changed = on_data_changed
        self.allow_management = allow_management

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()
        self._build_table()
        self.refresh()

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Заказы", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text=(
                "Менеджер видит список заказов. Администратор может "
                "добавлять, редактировать и удалять записи."
            ),
            justify="right",
        ).grid(row=0, column=1, sticky="e")

        if self.allow_management:
            buttons = ttk.Frame(header)
            buttons.grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))
            ttk.Button(buttons, text="Добавить заказ", command=self._add_order).pack(side="left")
            ttk.Button(buttons, text="Редактировать", command=self._edit_order).pack(
                side="left", padx=(8, 0)
            )
            ttk.Button(buttons, text="Удалить", command=self._delete_order).pack(
                side="left", padx=(8, 0)
            )

    def _build_table(self) -> None:
        columns = (
            "number",
            "order_date",
            "delivery_date",
            "pickup_point",
            "customer",
            "code",
            "status",
            "items",
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", lambda _event: self._show_details())

        headings = {
            "number": "Номер",
            "order_date": "Дата заказа",
            "delivery_date": "Дата доставки",
            "pickup_point": "Пункт выдачи",
            "customer": "Клиент",
            "code": "Код",
            "status": "Статус",
            "items": "Состав",
        }
        widths = {
            "number": 80,
            "order_date": 110,
            "delivery_date": 120,
            "pickup_point": 260,
            "customer": 220,
            "code": 90,
            "status": 120,
            "items": 240,
        }
        for key in columns:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor="center")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for order in self.db.list_orders():
            self.tree.insert(
                "",
                "end",
                iid=str(order["order_number"]),
                values=(
                    order["order_number"],
                    order["order_date"],
                    order["delivery_date"],
                    order["pickup_point_address"] or order["pickup_point_id"],
                    order["customer_name"],
                    order["pickup_code"],
                    order["status"],
                    order["items_text"],
                ),
            )

    def _selected_order_number(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return int(selected[0])

    def _show_details(self) -> None:
        order_number = self._selected_order_number()
        if order_number is None:
            return
        order = self.db.get_order(order_number)
        if order:
            OrderDetailsDialog(self, order)

    def _add_order(self) -> None:
        dialog = OrderFormDialog(self, self.db)
        self.wait_window(dialog)
        if dialog.saved:
            self.refresh()
            self.on_data_changed()

    def _edit_order(self) -> None:
        order_number = self._selected_order_number()
        if order_number is None:
            messagebox.showwarning("Нет выбора", "Сначала выберите заказ.")
            return
        dialog = OrderFormDialog(self, self.db, order_number=order_number)
        self.wait_window(dialog)
        if dialog.saved:
            self.refresh()
            self.on_data_changed()

    def _delete_order(self) -> None:
        order_number = self._selected_order_number()
        if order_number is None:
            messagebox.showwarning("Нет выбора", "Сначала выберите заказ.")
            return
        if not messagebox.askyesno("Подтверждение", f"Удалить заказ №{order_number}?"):
            return
        self.db.delete_order(order_number)
        self.refresh()
        self.on_data_changed()


class ProductFormDialog(tk.Toplevel):
    def __init__(
        self,
        master: tk.Widget,
        db: DatabaseManager,
        article: str | None = None,
    ) -> None:
        super().__init__(master)
        self.db = db
        self.original_article = article
        self.saved = False
        self.reference_data = self.db.get_product_reference_data()
        self.product = self.db.get_product(article) if article else None

        self.title("Карточка товара")
        self.geometry("760x560")
        self.configure(bg=THEME["background"])
        self.transient(master.winfo_toplevel())
        self.grab_set()

        self.vars = {
            "article": tk.StringVar(value=self._value("article")),
            "name": tk.StringVar(value=self._value("name")),
            "unit": tk.StringVar(value=self._value("unit")),
            "price": tk.StringVar(value=self._value("price")),
            "supplier": tk.StringVar(value=self._value("supplier")),
            "manufacturer": tk.StringVar(value=self._value("manufacturer")),
            "category": tk.StringVar(value=self._value("category")),
            "discount_percent": tk.StringVar(value=self._value("discount_percent")),
            "stock_quantity": tk.StringVar(value=self._value("stock_quantity")),
            "photo": tk.StringVar(value=self._value("photo")),
        }
        self._build_form()

    def _value(self, key: str) -> str:
        if not self.product:
            return ""
        value = self.product.get(key, "")
        return "" if value is None else str(value)

    def _build_form(self) -> None:
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        rows = [
            ("Артикул", "article", ttk.Entry),
            ("Наименование", "name", ttk.Entry),
            ("Единица измерения", "unit", ttk.Combobox),
            ("Цена", "price", ttk.Entry),
            ("Поставщик", "supplier", ttk.Combobox),
            ("Производитель", "manufacturer", ttk.Combobox),
            ("Категория", "category", ttk.Combobox),
            ("Скидка, %", "discount_percent", ttk.Entry),
            ("Остаток", "stock_quantity", ttk.Entry),
            ("Фото", "photo", ttk.Combobox),
        ]

        combo_values = {
            "unit": self.reference_data["units"],
            "supplier": self.reference_data["suppliers"],
            "manufacturer": self.reference_data["manufacturers"],
            "category": self.reference_data["categories"],
            "photo": [""] + sorted(
                set(
                    [
                        path.name
                        for path in PRODUCT_IMAGES_DIR.glob("*.jpg")
                        if path.stem.isdigit()
                    ]
                    + self.reference_data["photos"]
                )
            ),
        }

        for index, (label_text, key, widget_class) in enumerate(rows):
            ttk.Label(frame, text=label_text).grid(row=index, column=0, sticky="w", pady=6, padx=(0, 10))
            widget = widget_class(frame, textvariable=self.vars[key])
            if isinstance(widget, ttk.Combobox):
                widget.configure(values=combo_values.get(key, []), state="normal")
            widget.grid(row=index, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Описание").grid(row=len(rows), column=0, sticky="nw", pady=6)
        self.description_text = tk.Text(
            frame,
            height=6,
            font=("Times New Roman", 11),
            wrap="word",
            bg=THEME["surface"],
            fg=THEME["text"],
            relief="solid",
            bd=1,
        )
        self.description_text.grid(row=len(rows), column=1, sticky="nsew", pady=6)
        self.description_text.insert("1.0", self._value("description"))

        buttons = ttk.Frame(frame)
        buttons.grid(row=len(rows) + 1, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(buttons, text="Сохранить", style="Accent.TButton", command=self._save).pack(
            side="left"
        )
        ttk.Button(buttons, text="Отмена", command=self.destroy).pack(side="left", padx=(8, 0))

    def _save(self) -> None:
        payload = {key: variable.get() for key, variable in self.vars.items()}
        payload["description"] = self.description_text.get("1.0", "end")
        try:
            self.db.save_product(payload, original_article=self.original_article)
        except ValueError as exc:
            messagebox.showerror("Ошибка", str(exc), parent=self)
            return
        self.saved = True
        self.destroy()


class OrderFormDialog(tk.Toplevel):
    def __init__(
        self,
        master: tk.Widget,
        db: DatabaseManager,
        order_number: int | None = None,
    ) -> None:
        super().__init__(master)
        self.db = db
        self.original_number = order_number
        self.saved = False
        self.order = self.db.get_order(order_number) if order_number is not None else None
        self.pickup_points = self.db.get_pickup_points()
        self.users = self.db.get_users()
        self.user_choices = {
            "": "",
            **{
                f"{user['full_name']} ({user['role']})": str(user["id"])
                for user in self.users
            },
        }
        self.pickup_choices = {
            f"{point['id']}: {point['address']}": str(point["id"])
            for point in self.pickup_points
        }

        self.title("Карточка заказа")
        self.geometry("860x520")
        self.configure(bg=THEME["background"])
        self.transient(master.winfo_toplevel())
        self.grab_set()

        self.vars = {
            "order_number": tk.StringVar(value=self._value("order_number")),
            "items_text": tk.StringVar(value=self._value("items_text")),
            "order_date": tk.StringVar(value=self._value("order_date")),
            "delivery_date": tk.StringVar(value=self._value("delivery_date")),
            "pickup_point_display": tk.StringVar(value=self._pickup_display_value()),
            "customer_display": tk.StringVar(value=self._customer_display_value()),
            "customer_name": tk.StringVar(value=self._value("customer_name")),
            "pickup_code": tk.StringVar(value=self._value("pickup_code")),
            "status": tk.StringVar(value=self._value("status") or ORDER_STATUSES[0]),
        }

        self._build_form()

    def _value(self, key: str) -> str:
        if not self.order:
            return ""
        value = self.order.get(key, "")
        return "" if value is None else str(value)

    def _pickup_display_value(self) -> str:
        if not self.order:
            return next(iter(self.pickup_choices), "")
        for label, value in self.pickup_choices.items():
            if value == str(self.order["pickup_point_id"]):
                return label
        return next(iter(self.pickup_choices), "")

    def _customer_display_value(self) -> str:
        if not self.order or self.order.get("customer_user_id") is None:
            return ""
        for label, user_id in self.user_choices.items():
            if user_id == str(self.order["customer_user_id"]):
                return label
        return ""

    def _build_form(self) -> None:
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Номер заказа").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.vars["order_number"]).grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Состав заказа").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.vars["items_text"]).grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Label(frame, text="Формат: А112Т4, 2, F635R4, 1").grid(
            row=2, column=1, sticky="w", pady=(0, 6)
        )

        ttk.Label(frame, text="Дата заказа").grid(row=3, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.vars["order_date"]).grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Дата доставки").grid(row=4, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.vars["delivery_date"]).grid(row=4, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Пункт выдачи").grid(row=5, column=0, sticky="w", pady=6)
        pickup_combo = ttk.Combobox(
            frame,
            textvariable=self.vars["pickup_point_display"],
            values=list(self.pickup_choices.keys()),
            state="readonly",
        )
        pickup_combo.grid(row=5, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Пользователь").grid(row=6, column=0, sticky="w", pady=6)
        customer_combo = ttk.Combobox(
            frame,
            textvariable=self.vars["customer_display"],
            values=list(self.user_choices.keys()),
            state="readonly",
        )
        customer_combo.grid(row=6, column=1, sticky="ew", pady=6)
        customer_combo.bind("<<ComboboxSelected>>", self._fill_customer_name)

        ttk.Label(frame, text="ФИО клиента").grid(row=7, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.vars["customer_name"]).grid(
            row=7, column=1, sticky="ew", pady=6
        )

        ttk.Label(frame, text="Код получения").grid(row=8, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.vars["pickup_code"]).grid(row=8, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Статус").grid(row=9, column=0, sticky="w", pady=6)
        ttk.Combobox(
            frame,
            textvariable=self.vars["status"],
            values=ORDER_STATUSES,
            state="readonly",
        ).grid(row=9, column=1, sticky="ew", pady=6)

        buttons = ttk.Frame(frame)
        buttons.grid(row=10, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(buttons, text="Сохранить", style="Accent.TButton", command=self._save).pack(
            side="left"
        )
        ttk.Button(buttons, text="Отмена", command=self.destroy).pack(side="left", padx=(8, 0))

    def _fill_customer_name(self, _event: Any) -> None:
        selected = self.vars["customer_display"].get()
        user_id = self.user_choices.get(selected)
        if not user_id:
            return
        for user in self.users:
            if str(user["id"]) == user_id:
                self.vars["customer_name"].set(user["full_name"])
                return

    def _save(self) -> None:
        pickup_key = self.vars["pickup_point_display"].get()
        customer_key = self.vars["customer_display"].get()
        payload = {
            "order_number": self.vars["order_number"].get(),
            "items_text": self.vars["items_text"].get(),
            "order_date": self.vars["order_date"].get(),
            "delivery_date": self.vars["delivery_date"].get(),
            "pickup_point_id": self.pickup_choices.get(pickup_key, ""),
            "customer_user_id": self.user_choices.get(customer_key, ""),
            "customer_name": self.vars["customer_name"].get(),
            "pickup_code": self.vars["pickup_code"].get(),
            "status": self.vars["status"].get(),
        }
        try:
            self.db.save_order(payload, original_number=self.original_number)
        except ValueError as exc:
            messagebox.showerror("Ошибка", str(exc), parent=self)
            return
        self.saved = True
        self.destroy()


class ProductDetailsDialog(tk.Toplevel):
    def __init__(self, master: tk.Widget, product: dict[str, Any]) -> None:
        super().__init__(master)
        self.title(f"Товар {product['article']}")
        self.geometry("620x420")
        self.configure(bg=THEME["background"])
        self.transient(master.winfo_toplevel())

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        lines = [
            f"Артикул: {product['article']}",
            f"Наименование: {product['name']}",
            f"Категория: {product['category']}",
            f"Производитель: {product['manufacturer']}",
            f"Поставщик: {product['supplier']}",
            f"Цена: {format_money(product['price'])}",
            f"Скидка: {product['discount_percent']}%",
            f"Остаток: {product['stock_quantity']}",
            f"Фото: {product['photo'] or 'не указано'}",
            "",
            "Описание:",
            product["description"],
        ]
        ttk.Label(frame, text="\n".join(lines), justify="left", wraplength=560).pack(
            anchor="w"
        )
        ttk.Button(frame, text="Закрыть", command=self.destroy).pack(anchor="e", pady=(16, 0))


class OrderDetailsDialog(tk.Toplevel):
    def __init__(self, master: tk.Widget, order: dict[str, Any]) -> None:
        super().__init__(master)
        self.title(f"Заказ №{order['order_number']}")
        self.geometry("620x340")
        self.configure(bg=THEME["background"])
        self.transient(master.winfo_toplevel())

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        lines = [
            f"Номер: {order['order_number']}",
            f"Дата заказа: {order['order_date']}",
            f"Дата доставки: {order['delivery_date']}",
            f"Пункт выдачи: {order.get('pickup_point_address') or order['pickup_point_id']}",
            f"Клиент: {order['customer_name']}",
            f"Код получения: {order['pickup_code']}",
            f"Статус: {order['status']}",
            "",
            "Состав заказа:",
            order["items_text"],
        ]
        ttk.Label(frame, text="\n".join(lines), justify="left", wraplength=560).pack(
            anchor="w"
        )
        ttk.Button(frame, text="Закрыть", command=self.destroy).pack(anchor="e", pady=(16, 0))
