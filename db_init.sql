-- -----------------------------------------------------
-- DATABASE: rental
-- -----------------------------------------------------
DROP DATABASE IF EXISTS rental;
CREATE DATABASE rental;
USE rental;

-- -----------------------------------------------------
-- ADMINS TABLE 
-- -----------------------------------------------------
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

:
INSERT INTO admins (username, password)
VALUES ('admin', 'admin123');

-- -----------------------------------------------------
-- VEHICLES TABLE
-- -----------------------------------------------------
CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reg_no VARCHAR(255),
    make VARCHAR(255),
    model VARCHAR(255),
    year INT,
    rate_per_day DECIMAL(10,2),
    status VARCHAR(50)
);

INSERT INTO vehicles (reg_no, make, model, year, rate_per_day, status)
VALUES 
('RJ14AB1234', 'Toyota', 'Innova', 2020, 1500, 'available'),
('DL10CD5678', 'Hyundai', 'Creta', 2019, 1200, 'available'),
('MH12EF9999', 'Maruti', 'Swift', 2021, 900, 'available');

-- -----------------------------------------------------
-- CUSTOMERS TABLE
-- -----------------------------------------------------
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255)
);

INSERT INTO customers (name, phone, email)
VALUES
('Rahul Sharma', '9876543210', 'rahul@example.com'),
('Priya Kapoor', '9123456789', 'priya@example.com');

-- -----------------------------------------------------
-- RENTALS TABLE
-- -----------------------------------------------------
CREATE TABLE rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    customer_id INT,
    start_date DATE,
    expected_return_date DATE,
    actual_return_date DATE NULL,
    status VARCHAR(50),
    amount DECIMAL(12,2) NULL,

    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);


INSERT INTO rentals (vehicle_id, customer_id, start_date, expected_return_date, actual_return_date, status, amount)
VALUES (1, 1, '2025-01-01', '2025-01-03', NULL, 'ongoing', 4500.00);

