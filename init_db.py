import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Products table
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image TEXT
)
''')

# Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')
# Sample products with correct paths
sample_products = [
    ('Laptop', 'High-performance laptop with 16GB RAM and 512GB SSD', 50000, 'images/products/laptop.jpeg'),
    ('Smartphone', 'Latest smartphone with OLED display and 128GB storage', 20000, 'images/products/phone.jpeg'),
    ('Headphones', 'Wireless noise-cancelling headphones', 5000, 'images/products/headphones.jpeg'),
    ('Smartwatch', 'Waterproof smartwatch with heart rate monitor', 7000, 'images/products/smartwatch.jpeg')
]

for product in sample_products:
    c.execute("INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)", product)


c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')

conn.commit()
conn.close()
print("Database created and sample products added!")
