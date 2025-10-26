-- ============================================
-- Модуль 6: Тестові дані для навчання SQL
-- ============================================

-- ============================================
-- 1. Відділи
-- ============================================

INSERT INTO departments (name, location) VALUES
('Sales', 'Kyiv'),
('IT', 'Lviv'),
('Marketing', 'Kyiv'),
('HR', 'Kharkiv'),
('Finance', 'Odesa'),
('Customer Support', 'Dnipro');

-- ============================================
-- 2. Співробітники
-- ============================================

INSERT INTO employees (first_name, last_name, email, phone, department_id, salary, hire_date, is_active) VALUES
('Olena', 'Kovalenko', 'olena.kovalenko@company.ua', '+380501234567', 1, 45000, '2020-03-15', TRUE),
('Andriy', 'Shevchenko', 'andriy.shevchenko@company.ua', '+380502345678', 2, 65000, '2019-01-10', TRUE),
('Mariya', 'Petrenko', 'mariya.petrenko@company.ua', '+380503456789', 3, 42000, '2021-06-20', TRUE),
('Ivan', 'Bondarenko', 'ivan.bondarenko@company.ua', '+380504567890', 2, 58000, '2020-08-05', TRUE),
('Oksana', 'Melnyk', 'oksana.melnyk@company.ua', '+380505678901', 4, 40000, '2022-02-14', TRUE),
('Dmytro', 'Tkachenko', 'dmytro.tkachenko@company.ua', '+380506789012', 1, 48000, '2021-11-30', TRUE),
('Yulia', 'Kravchenko', 'yulia.kravchenko@company.ua', '+380507890123', 5, 52000, '2020-05-22', TRUE),
('Sergiy', 'Moroz', 'sergiy.moroz@company.ua', '+380508901234', 2, 70000, '2018-09-12', TRUE),
('Natalia', 'Lysenko', 'natalia.lysenko@company.ua', '+380509012345', 6, 38000, '2022-07-01', TRUE),
('Viktor', 'Savchenko', 'viktor.savchenko@company.ua', '+380500123456', 3, 44000, '2021-03-18', TRUE),
('Tetiana', 'Marchenko', 'tetiana.marchenko@company.ua', '+380501122334', 1, 46000, '2020-10-25', TRUE),
('Oleksandr', 'Koval', 'oleksandr.koval@company.ua', '+380502233445', 2, 62000, '2019-12-05', FALSE);

-- ============================================
-- 3. Клієнти
-- ============================================

INSERT INTO customers (first_name, last_name, email, phone, city, country, registration_date) VALUES
('Petro', 'Ivanov', 'petro.ivanov@gmail.com', '+380671234567', 'Kyiv', 'Ukraine', '2023-01-15'),
('Anna', 'Sidorenko', 'anna.sidorenko@gmail.com', '+380672345678', 'Lviv', 'Ukraine', '2023-02-20'),
('Maksym', 'Kovalchuk', 'maksym.kovalchuk@gmail.com', '+380673456789', 'Kharkiv', 'Ukraine', '2023-03-10'),
('Iryna', 'Bondar', 'iryna.bondar@gmail.com', '+380674567890', 'Odesa', 'Ukraine', '2023-01-25'),
('Bohdan', 'Kravets', 'bohdan.kravets@gmail.com', '+380675678901', 'Dnipro', 'Ukraine', '2023-04-12'),
('Olha', 'Rudenko', 'olha.rudenko@gmail.com', '+380676789012', 'Kyiv', 'Ukraine', '2023-02-28'),
('Taras', 'Melnychuk', 'taras.melnychuk@gmail.com', '+380677890123', 'Zaporizhzhia', 'Ukraine', '2023-05-05'),
('Kateryna', 'Polishchuk', 'kateryna.polishchuk@gmail.com', '+380678901234', 'Lviv', 'Ukraine', '2023-03-22'),
('Vasyl', 'Shevchuk', 'vasyl.shevchuk@gmail.com', '+380679012345', 'Kyiv', 'Ukraine', '2023-06-14'),
('Halyna', 'Tkach', 'halyna.tkach@gmail.com', '+380670123456', 'Vinnytsia', 'Ukraine', '2023-04-30');

-- ============================================
-- 4. Категорії товарів
-- ============================================

INSERT INTO categories (name, description, parent_category_id) VALUES
('Electronics', 'Електронні пристрої та гаджети', NULL),
('Computers', 'Ноутбуки, ПК та комплектуючі', 1),
('Smartphones', 'Смартфони та аксесуари', 1),
('Home & Garden', 'Товари для дому та саду', NULL),
('Kitchen', 'Кухонне приладдя', 4),
('Books', 'Книги різних жанрів', NULL),
('Clothing', 'Одяг та взуття', NULL);

-- ============================================
-- 5. Товари
-- ============================================

INSERT INTO products (name, description, category_id, price, stock_quantity, is_available) VALUES
('Laptop HP Pavilion', 'Ноутбук з процесором Intel Core i5, 8GB RAM, 256GB SSD', 2, 18999.00, 15, TRUE),
('iPhone 14 Pro', 'Смартфон Apple з камерою 48MP', 3, 39999.00, 8, TRUE),
('Samsung Galaxy S23', 'Флагманський смартфон Samsung', 3, 29999.00, 12, TRUE),
('Dell XPS 13', 'Ультрабук преміум класу', 2, 35999.00, 5, TRUE),
('Coffee Maker DeLonghi', 'Автоматична кавоварка', 5, 8999.00, 20, TRUE),
('Air Fryer Philips', 'Аерогриль 4.1L', 5, 3499.00, 25, TRUE),
('Blender Vitamix', 'Професійний блендер', 5, 12999.00, 10, TRUE),
('The Psychology of Money', 'Книга про фінансову психологію', 6, 399.00, 50, TRUE),
('Atomic Habits', 'Книга про формування звичок (англійською)', 6, 459.00, 35, TRUE),
('MacBook Air M2', 'Ноутбук Apple з процесором M2', 2, 49999.00, 6, TRUE),
('AirPods Pro 2', 'Бездротові навушники Apple', 3, 8999.00, 30, TRUE),
('Gaming Chair', 'Геймерське крісло з підсвіткою', 4, 5499.00, 18, TRUE),
('Standing Desk', 'Регульований стіл для роботи стоячи', 4, 9999.00, 7, TRUE),
('Wireless Mouse Logitech', 'Бездротова миша MX Master 3', 2, 2799.00, 40, TRUE),
('Mechanical Keyboard', 'Механічна клавіатура з RGB', 2, 3299.00, 22, TRUE),
('Smart Watch Garmin', 'Спортивний годинник з GPS', 1, 12999.00, 14, TRUE),
('Tablet iPad Air', 'Планшет Apple 10.9"', 1, 24999.00, 11, TRUE),
('Hoodie Nike', 'Спортивна толстовка', 7, 1899.00, 45, TRUE),
('Running Shoes Adidas', 'Кросівки для бігу', 7, 2999.00, 28, TRUE);

-- ============================================
-- 6. Замовлення
-- ============================================

INSERT INTO orders (customer_id, employee_id, order_date, status, shipping_address) VALUES
(1, 1, '2024-10-01 10:30:00', 'delivered', 'вул. Хрещатик, 1, Київ'),
(2, 1, '2024-10-02 14:20:00', 'delivered', 'вул. Шевченка, 15, Львів'),
(3, 6, '2024-10-03 09:15:00', 'delivered', 'просп. Науки, 23, Харків'),
(4, 6, '2024-10-05 16:45:00', 'shipped', 'вул. Дерибасівська, 8, Одеса'),
(1, 11, '2024-10-07 11:30:00', 'processing', 'вул. Хрещатик, 1, Київ'),
(5, 1, '2024-10-08 13:00:00', 'delivered', 'вул. Січових Стрільців, 12, Дніпро'),
(6, 6, '2024-10-10 10:00:00', 'processing', 'вул. Саксаганського, 45, Київ'),
(7, 11, '2024-10-12 15:30:00', 'pending', 'просп. Соборний, 67, Запоріжжя'),
(8, 1, '2024-10-14 12:45:00', 'shipped', 'вул. Личаківська, 89, Львів'),
(9, 6, '2024-10-15 09:20:00', 'processing', 'вул. Велика Васильківська, 34, Київ');

-- ============================================
-- 7. Позиції замовлень
-- ============================================

INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES
-- Замовлення 1
(1, 1, 1, 18999.00),
(1, 14, 1, 2799.00),
(1, 15, 1, 3299.00),
-- Замовлення 2
(2, 3, 1, 29999.00),
(2, 11, 2, 8999.00),
-- Замовлення 3
(3, 5, 1, 8999.00),
(3, 6, 1, 3499.00),
(3, 8, 2, 399.00),
-- Замовлення 4
(4, 4, 1, 35999.00),
(4, 14, 1, 2799.00),
-- Замовлення 5
(5, 2, 1, 39999.00),
(5, 11, 1, 8999.00),
-- Замовлення 6
(6, 12, 2, 5499.00),
(6, 18, 3, 1899.00),
-- Замовлення 7
(7, 7, 1, 12999.00),
(7, 6, 1, 3499.00),
-- Замовлення 8
(8, 16, 1, 12999.00),
(8, 19, 2, 2999.00),
-- Замовлення 9
(9, 17, 1, 24999.00),
(9, 11, 1, 8999.00),
-- Замовлення 10
(10, 10, 1, 49999.00),
(10, 11, 1, 8999.00);

-- ============================================
-- Оновити total_amount в замовленнях
-- ============================================

UPDATE orders o
SET total_amount = (
    SELECT SUM(subtotal)
    FROM order_items oi
    WHERE oi.order_id = o.id
);

-- ============================================
-- Перевірка даних
-- ============================================

-- Показати статистику
SELECT 'Departments' as table_name, COUNT(*) as count FROM departments
UNION ALL
SELECT 'Employees', COUNT(*) FROM employees
UNION ALL
SELECT 'Customers', COUNT(*) FROM customers
UNION ALL
SELECT 'Categories', COUNT(*) FROM categories
UNION ALL
SELECT 'Products', COUNT(*) FROM products
UNION ALL
SELECT 'Orders', COUNT(*) FROM orders
UNION ALL
SELECT 'Order Items', COUNT(*) FROM order_items;

-- ============================================
-- Готово! База даних заповнена тестовими даними
-- ============================================
