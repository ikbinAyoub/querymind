-- Demo Database Initialization Script
-- This creates sample tables for testing the SQL-RAG system

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'pending'
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

-- Insert sample data
INSERT INTO users (username, email, full_name) VALUES
    ('john_doe', 'john@example.com', 'John Doe'),
    ('jane_smith', 'jane@example.com', 'Jane Smith'),
    ('bob_wilson', 'bob@example.com', 'Bob Wilson'),
    ('alice_jones', 'alice@example.com', 'Alice Jones'),
    ('charlie_brown', 'charlie@example.com', 'Charlie Brown');

INSERT INTO products (name, description, price, category, stock_quantity) VALUES
    ('Laptop Pro', 'High-performance laptop', 1299.99, 'Electronics', 50),
    ('Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 'Electronics', 200),
    ('USB-C Hub', '7-in-1 USB-C hub', 49.99, 'Electronics', 150),
    ('Mechanical Keyboard', 'RGB mechanical keyboard', 89.99, 'Electronics', 75),
    ('Monitor 27"', '4K IPS monitor', 399.99, 'Electronics', 30),
    ('Desk Lamp', 'LED desk lamp with dimmer', 34.99, 'Home Office', 100),
    ('Office Chair', 'Ergonomic office chair', 249.99, 'Furniture', 25),
    ('Standing Desk', 'Electric standing desk', 499.99, 'Furniture', 15),
    ('Notebook Set', 'Premium notebook set', 19.99, 'Stationery', 300),
    ('Pen Pack', 'Professional pen pack', 12.99, 'Stationery', 500);

INSERT INTO orders (user_id, total_amount, status) VALUES
    (1, 1379.98, 'completed'),
    (2, 539.97, 'completed'),
    (3, 89.99, 'pending'),
    (1, 299.98, 'shipped'),
    (4, 1749.97, 'completed'),
    (5, 64.97, 'pending');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 1299.99),
    (1, 2, 2, 29.99),
    (1, 3, 1, 49.99),
    (2, 5, 1, 399.99),
    (2, 4, 1, 89.99),
    (2, 3, 1, 49.99),
    (3, 4, 1, 89.99),
    (4, 7, 1, 249.99),
    (4, 3, 1, 49.99),
    (5, 1, 1, 1299.99),
    (5, 5, 1, 399.99),
    (5, 3, 1, 49.99),
    (6, 6, 1, 34.99),
    (6, 2, 1, 29.99);

-- Add comments to tables and columns
COMMENT ON TABLE users IS 'User accounts for the e-commerce system';
COMMENT ON TABLE products IS 'Product catalog with inventory';
COMMENT ON TABLE orders IS 'Customer orders';
COMMENT ON TABLE order_items IS 'Individual items within each order';

COMMENT ON COLUMN users.id IS 'Unique user identifier';
COMMENT ON COLUMN products.price IS 'Product price in USD';
COMMENT ON COLUMN orders.status IS 'Order status: pending, shipped, completed, cancelled';
