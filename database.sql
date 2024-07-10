CREATE DATABASE xxx4;
USE xxx4;

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

ALTER TABLE users

ADD COLUMN fullname VARCHAR(255) AFTER password;

 


CREATE TABLE IF NOT EXISTS accounts (
    user_id INT PRIMARY KEY,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
select * from users;


CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    full_name VARCHAR(200)
);

INSERT INTO admin (name, email, password, full_name) VALUES
('admin1', 'admin1@example.com', 'password1', 'Admin One'),
('admin2', 'admin2@example.com', 'password2', 'Admin Two'),
('admin3', 'admin3@example.com', 'password3', 'Admin Three');

select * from admin;

drop table exchange_rates;
drop table transactions;
drop table accounts;
drop table users;
select * from transactions;
select * from users;
select* from accounts

