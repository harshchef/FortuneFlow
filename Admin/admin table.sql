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