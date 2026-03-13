BEGIN TRANSACTION;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
CREATE TABLE pickup_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE
);
CREATE TABLE products (
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
CREATE TABLE orders (
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
    FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (customer_user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_article TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_article) REFERENCES products(article) ON UPDATE CASCADE ON DELETE RESTRICT
);
INSERT INTO users VALUES(1,'Никифорова Весения Николаевна','94d5ous@gmail.com','uzWC67','Администратор');
INSERT INTO users VALUES(2,'Сазонов Руслан Германович','uth4iz@mail.com','2L6KZG','Администратор');
INSERT INTO users VALUES(3,'Одинцов Серафим Артёмович','yzls62@outlook.com','JlFRCZ','Администратор');
INSERT INTO users VALUES(4,'Степанов Михаил Артёмович','1diph5e@tutanota.com','8ntwUp','Менеджер');
INSERT INTO users VALUES(5,'Ворсин Петр Евгеньевич','tjde7c@yahoo.com','YOyhfR','Менеджер');
INSERT INTO users VALUES(6,'Старикова Елена Павловна','wpmrc3do@tutanota.com','RSbvHv','Менеджер');
INSERT INTO users VALUES(7,'Михайлюк Анна Вячеславовна','5d4zbu@tutanota.com','rwVDh9','Авторизированный клиент');
INSERT INTO users VALUES(8,'Ситдикова Елена Анатольевна','ptec8ym@yahoo.com','LdNyos','Авторизированный клиент');
INSERT INTO users VALUES(9,'Ворсин Петр Евгеньевич','1qz4kw@mail.com','gynQMT','Авторизированный клиент');
INSERT INTO users VALUES(10,'Старикова Елена Павловна','4np6se@mail.com','AtnDjr','Авторизированный клиент');
INSERT INTO pickup_points VALUES(1,'420151, г. Лесной, ул. Вишневая, 32');
INSERT INTO pickup_points VALUES(2,'125061, г. Лесной, ул. Подгорная, 8');
INSERT INTO pickup_points VALUES(3,'630370, г. Лесной, ул. Шоссейная, 24');
INSERT INTO pickup_points VALUES(4,'400562, г. Лесной, ул. Зеленая, 32');
INSERT INTO pickup_points VALUES(5,'614510, г. Лесной, ул. Маяковского, 47');
INSERT INTO pickup_points VALUES(6,'410542, г. Лесной, ул. Светлая, 46');
INSERT INTO pickup_points VALUES(7,'620839, г. Лесной, ул. Цветочная, 8');
INSERT INTO pickup_points VALUES(8,'443890, г. Лесной, ул. Коммунистическая, 1');
INSERT INTO pickup_points VALUES(9,'603379, г. Лесной, ул. Спортивная, 46');
INSERT INTO pickup_points VALUES(10,'603721, г. Лесной, ул. Гоголя, 41');
INSERT INTO pickup_points VALUES(11,'410172, г. Лесной, ул. Северная, 13');
INSERT INTO pickup_points VALUES(12,'614611, г. Лесной, ул. Молодежная, 50');
INSERT INTO pickup_points VALUES(13,'454311, г.Лесной, ул. Новая, 19');
INSERT INTO pickup_points VALUES(14,'660007, г.Лесной, ул. Октябрьская, 19');
INSERT INTO pickup_points VALUES(15,'603036, г. Лесной, ул. Садовая, 4');
INSERT INTO pickup_points VALUES(16,'394060, г.Лесной, ул. Фрунзе, 43');
INSERT INTO pickup_points VALUES(17,'410661, г. Лесной, ул. Школьная, 50');
INSERT INTO pickup_points VALUES(18,'625590, г. Лесной, ул. Коммунистическая, 20');
INSERT INTO pickup_points VALUES(19,'625683, г. Лесной, ул. 8 Марта');
INSERT INTO pickup_points VALUES(20,'450983, г.Лесной, ул. Комсомольская, 26');
INSERT INTO pickup_points VALUES(21,'394782, г. Лесной, ул. Чехова, 3');
INSERT INTO pickup_points VALUES(22,'603002, г. Лесной, ул. Дзержинского, 28');
INSERT INTO pickup_points VALUES(23,'450558, г. Лесной, ул. Набережная, 30');
INSERT INTO pickup_points VALUES(24,'344288, г. Лесной, ул. Чехова, 1');
INSERT INTO pickup_points VALUES(25,'614164, г.Лесной,  ул. Степная, 30');
INSERT INTO pickup_points VALUES(26,'394242, г. Лесной, ул. Коммунистическая, 43');
INSERT INTO pickup_points VALUES(27,'660540, г. Лесной, ул. Солнечная, 25');
INSERT INTO pickup_points VALUES(28,'125837, г. Лесной, ул. Шоссейная, 40');
INSERT INTO pickup_points VALUES(29,'125703, г. Лесной, ул. Партизанская, 49');
INSERT INTO pickup_points VALUES(30,'625283, г. Лесной, ул. Победы, 46');
INSERT INTO pickup_points VALUES(31,'614753, г. Лесной, ул. Полевая, 35');
INSERT INTO pickup_points VALUES(32,'426030, г. Лесной, ул. Маяковского, 44');
INSERT INTO pickup_points VALUES(33,'450375, г. Лесной ул. Клубная, 44');
INSERT INTO pickup_points VALUES(34,'625560, г. Лесной, ул. Некрасова, 12');
INSERT INTO pickup_points VALUES(35,'630201, г. Лесной, ул. Комсомольская, 17');
INSERT INTO pickup_points VALUES(36,'190949, г. Лесной, ул. Мичурина, 26');
INSERT INTO products VALUES('А112Т4','Ботинки','шт.',4990,'Kari','Kari','Женская обувь',3,6,'Женские Ботинки демисезонные kari','1.jpg');
INSERT INTO products VALUES('F635R4','Ботинки','шт.',3244,'Обувь для вас','Marco Tozzi','Женская обувь',2,13,'Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый','2.jpg');
INSERT INTO products VALUES('H782T5','Туфли','шт.',4499,'Kari','Kari','Мужская обувь',4,5,'Туфли kari мужские классика MYZ21AW-450A, размер 43, цвет: черный','3.jpg');
INSERT INTO products VALUES('G783F5','Ботинки','шт.',5900,'Kari','Рос','Мужская обувь',2,8,'Мужские ботинки Рос-Обувь кожаные с натуральным мехом','4.jpg');
INSERT INTO products VALUES('J384T6','Ботинки','шт.',3800,'Обувь для вас','Rieker','Мужская обувь',2,16,'B3430/14 Полуботинки мужские Rieker','5.jpg');
INSERT INTO products VALUES('D572U8','Кроссовки','шт.',4100,'Обувь для вас','Рос','Мужская обувь',3,6,'129615-4 Кроссовки мужские','6.jpg');
INSERT INTO products VALUES('F572H7','Туфли','шт.',2700,'Kari','Marco Tozzi','Женская обувь',2,14,'Туфли Marco Tozzi женские летние, размер 39, цвет черный','7.jpg');
INSERT INTO products VALUES('D329H3','Полуботинки','шт.',1890,'Обувь для вас','Alessio Nesca','Женская обувь',4,4,'Полуботинки Alessio Nesca женские 3-30797-47, размер 37, цвет: бордовый','8.jpg');
INSERT INTO products VALUES('B320R5','Туфли','шт.',4300,'Kari','Rieker','Женская обувь',2,6,'Туфли Rieker женские демисезонные, размер 41, цвет коричневый','9.jpg');
INSERT INTO products VALUES('G432E4','Туфли','шт.',2800,'Kari','Kari','Женская обувь',3,15,'Туфли kari женские TR-YR-413017, размер 37, цвет: черный','10.jpg');
INSERT INTO products VALUES('S213E3','Полуботинки','шт.',2156,'Обувь для вас','CROSBY','Мужская обувь',3,6,'407700/01-01 Полуботинки мужские CROSBY','');
INSERT INTO products VALUES('E482R4','Полуботинки','шт.',1800,'Kari','Kari','Женская обувь',2,14,'Полуботинки kari женские MYZ20S-149, размер 41, цвет: черный','');
INSERT INTO products VALUES('S634B5','Кеды','шт.',5500,'Обувь для вас','CROSBY','Мужская обувь',3,0,'Кеды Caprice мужские демисезонные, размер 42, цвет черный','');
INSERT INTO products VALUES('K345R4','Полуботинки','шт.',2100,'Обувь для вас','CROSBY','Мужская обувь',2,3,'407700/01-02 Полуботинки мужские CROSBY','');
INSERT INTO products VALUES('O754F4','Туфли','шт.',5400,'Обувь для вас','Rieker','Женская обувь',4,18,'Туфли женские демисезонные Rieker артикул 55073-68/37','');
INSERT INTO products VALUES('G531F4','Ботинки','шт.',6600,'Kari','Kari','Женская обувь',12,9,'Ботинки женские зимние ROMER арт. 893167-01 Черный','');
INSERT INTO products VALUES('J542F5','Тапочки','шт.',500,'Kari','Kari','Мужская обувь',13,0,'Тапочки мужские Арт.70701-55-67син р.41','');
INSERT INTO products VALUES('B431R5','Ботинки','шт.',2700,'Обувь для вас','Rieker','Мужская обувь',2,5,'Мужские кожаные ботинки/мужские ботинки','');
INSERT INTO products VALUES('P764G4','Туфли','шт.',6800,'Kari','CROSBY','Женская обувь',15,15,'Туфли женские, ARGO, размер 38','');
INSERT INTO products VALUES('C436G5','Ботинки','шт.',10200,'Kari','Alessio Nesca','Женская обувь',15,9,'Ботинки женские, ARGO, размер 40','');
INSERT INTO products VALUES('F427R5','Ботинки','шт.',11800,'Обувь для вас','Rieker','Женская обувь',15,11,'Ботинки на молнии с декоративной пряжкой FRAU','');
INSERT INTO products VALUES('N457T5','Полуботинки','шт.',4600,'Kari','CROSBY','Женская обувь',3,13,'Полуботинки Ботинки черные зимние, мех','');
INSERT INTO products VALUES('D364R4','Туфли','шт.',12400,'Kari','Kari','Женская обувь',16,5,'Туфли Luiza Belly женские Kate-lazo черные из натуральной замши','');
INSERT INTO products VALUES('S326R5','Тапочки','шт.',9900,'Обувь для вас','CROSBY','Мужская обувь',17,15,'Мужские кожаные тапочки "Профиль С.Дали"','');
INSERT INTO products VALUES('L754R4','Полуботинки','шт.',1700,'Kari','Kari','Женская обувь',2,7,'Полуботинки kari женские WB2020SS-26, размер 38, цвет: черный','');
INSERT INTO products VALUES('M542T5','Кроссовки','шт.',2800,'Обувь для вас','Rieker','Мужская обувь',18,3,'Кроссовки мужские TOFA','');
INSERT INTO products VALUES('D268G5','Туфли','шт.',4399,'Обувь для вас','Rieker','Женская обувь',3,12,'Туфли Rieker женские демисезонные, размер 36, цвет коричневый','');
INSERT INTO products VALUES('T324F5','Сапоги','шт.',4699,'Kari','CROSBY','Женская обувь',2,5,'Сапоги замша Цвет: синий','');
INSERT INTO products VALUES('K358H6','Тапочки','шт.',599,'Kari','Rieker','Мужская обувь',20,2,'Тапочки мужские син р.41','');
INSERT INTO products VALUES('H535R5','Ботинки','шт.',2300,'Обувь для вас','Rieker','Женская обувь',2,7,'Женские Ботинки демисезонные','');
INSERT INTO orders VALUES(1,1,'А112Т4, 2, F635R4, 2','27.02.2025','20.04.2025',1,'Степанов Михаил Артёмович',4,'901','Завершен');
INSERT INTO orders VALUES(2,2,'H782T5, 1, G783F5, 1','28.09.2022','21.04.2025',11,'Никифорова Весения Николаевна',1,'902','Завершен');
INSERT INTO orders VALUES(3,3,'J384T6, 10, D572U8, 10','21.03.2025','22.04.2025',2,'Сазонов Руслан Германович',2,'903','Завершен');
INSERT INTO orders VALUES(4,4,'F572H7, 5, D329H3, 4','20.02.2025','23.04.2025',11,'Одинцов Серафим Артёмович',3,'904','Завершен');
INSERT INTO orders VALUES(5,5,'А112Т4, 2, F635R4, 2','17.03.2025','24.04.2025',2,'Степанов Михаил Артёмович',4,'905','Завершен');
INSERT INTO orders VALUES(6,6,'H782T5, 1, G783F5, 1','01.03.2025','25.04.2025',15,'Никифорова Весения Николаевна',1,'906','Завершен');
INSERT INTO orders VALUES(7,7,'J384T6, 10, D572U8, 10','30.02.2025','26.04.2025',3,'Сазонов Руслан Германович',2,'907','Завершен');
INSERT INTO orders VALUES(8,8,'F572H7, 5, D329H3, 4','31.03.2025','27.04.2025',19,'Одинцов Серафим Артёмович',3,'908','Новый');
INSERT INTO orders VALUES(9,9,'B320R5, 5, G432E4, 1','02.04.2025','28.04.2025',5,'Степанов Михаил Артёмович',4,'909','Новый');
INSERT INTO orders VALUES(10,10,'S213E3, 5, E482R4, 5','03.04.2025','29.04.2025',19,'Степанов Михаил Артёмович',4,'910','Новый');
INSERT INTO order_items VALUES(1,1,'А112Т4',2);
INSERT INTO order_items VALUES(2,1,'F635R4',2);
INSERT INTO order_items VALUES(3,2,'H782T5',1);
INSERT INTO order_items VALUES(4,2,'G783F5',1);
INSERT INTO order_items VALUES(5,3,'J384T6',10);
INSERT INTO order_items VALUES(6,3,'D572U8',10);
INSERT INTO order_items VALUES(7,4,'F572H7',5);
INSERT INTO order_items VALUES(8,4,'D329H3',4);
INSERT INTO order_items VALUES(9,5,'А112Т4',2);
INSERT INTO order_items VALUES(10,5,'F635R4',2);
INSERT INTO order_items VALUES(11,6,'H782T5',1);
INSERT INTO order_items VALUES(12,6,'G783F5',1);
INSERT INTO order_items VALUES(13,7,'J384T6',10);
INSERT INTO order_items VALUES(14,7,'D572U8',10);
INSERT INTO order_items VALUES(15,8,'F572H7',5);
INSERT INTO order_items VALUES(16,8,'D329H3',4);
INSERT INTO order_items VALUES(17,9,'B320R5',5);
INSERT INTO order_items VALUES(18,9,'G432E4',1);
INSERT INTO order_items VALUES(19,10,'S213E3',5);
INSERT INTO order_items VALUES(20,10,'E482R4',5);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_status ON orders(status);
COMMIT;
