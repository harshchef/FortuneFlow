Create Database xxx;
use xxx;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    country_of_residence VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    sender_currency VARCHAR(10) NOT NULL,
    receiver_currency VARCHAR(10) NOT NULL,
    exchange_rate DECIMAL(10, 6) NOT NULL,
    converted_amount DECIMAL(10, 2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS exchange_rates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    target_currency VARCHAR(10) NOT NULL,
    rate DECIMAL(10, 6) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (base_currency, target_currency)
);



INSERT INTO transactions (sender_id, receiver_id, amount, sender_currency, receiver_currency, exchange_rate, converted_amount)
VALUES
    (1, 2, 100.00, 'USD', 'EUR', 0.85, 85.00),
    (2, 1, 50.00, 'EUR', 'USD', 1.18, 59.00),
    (3, 2, 75.00, 'GBP', 'EUR', 1.10, 82.50);
INSERT INTO users (username, email, password, country_of_residence)
VALUES
    ('John Doe', 'john@example.com', 'password123', 'USA'),
    ('Jane Smith', 'jane@example.com', 'password456', 'Canada'),
    ('Mike Johnson', 'mike@example.com', 'password789', 'UK');



drop table exchange_rates;
drop table transactions;
drop table users;
select * from transactions;

